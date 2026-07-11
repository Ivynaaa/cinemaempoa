import hashlib
import imghdr
import os
from datetime import datetime
from io import BytesIO
from typing import List, Optional, Tuple

import requests
from PIL import Image, UnidentifiedImageError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from werkzeug.utils import secure_filename

from flask_backend.env_config import APP_ENVIRONMENT
from flask_backend.import_json import ScrappedCinema, ScrappedFeature, ScrappedResult
from flask_backend.models import ScreeningDate
from flask_backend.repository.cinemas import get_by_slug as get_cinema_by_slug
from flask_backend.repository.movies import (
    get_by_title_or_create as get_movie_by_title_or_create,
)
from flask_backend.repository.screenings import (
    create as create_screening,
    get_by_movie_id_and_cinema_id as get_screening_by_movie_id_and_cinema_id,
    update_screening_dates,
)
from flask_backend.service.upload import upload_image_to_api, upload_image_to_local_disk
from flask_backend.utils.enums.environment import EnvironmentEnum

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def _check_if_actually_image(file):
    header = file.read(512)
    file.seek(0)
    format = imghdr.what(None, header)
    return format in ALLOWED_EXTENSIONS


def _allowed_extension(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_image(file) -> tuple[bool, str]:
    """Receives an uploaded file and returns whether it is valid
    based on the application rules"""
    filename = secure_filename(file.filename)
    if not _allowed_extension(filename):
        return (
            False,
            f"Extensão do arquivo inválida. Aceitamos {', '.join(ALLOWED_EXTENSIONS)}.",
        )
    if not _check_if_actually_image(file.stream):
        return (False, "Arquivo corrompido ou inválido.")
    return True, None


def save_image(file, app, filename: Optional[str] = None) -> Tuple[str, int, int]:
    """Saves the received `file` into disk or uploads it to imgBB API,
    depending on the current environment"""
    # always save images locally on development
    if APP_ENVIRONMENT != EnvironmentEnum.PRODUCTION:
        return upload_image_to_local_disk(file, app, filename)
    # on production, attempt to save to the imgBB API
    try:
        return upload_image_to_api(app, file)
    # on failure, save locally
    except requests.exceptions.HTTPError:
        file.seek(0)
        return upload_image_to_local_disk(file, app, filename)


def build_dates(screening_dates: List[str]) -> List[ScreeningDate]:
    """Receives a list of datetime strings in format ['2023-11-11T19:00', '2023-11-11T19:00']
    and returns a list of ScreeningDate objects.

    Raises
        ValueError: string elements in received list are not in %Y-%m-%dT%H:%M format"""
    screening_date_objects = []
    for screening_date in screening_dates:
        # Remove seconds from the string before parsing
        screening_date = screening_date[:16]  # Keeps up to YYYY-MM-DDTHH:MM
        try:
            parsed_screening_date = datetime.strptime(screening_date, "%Y-%m-%dT%H:%M")
        except ValueError:
            parsed_screening_date = datetime.strptime(screening_date, "%Y-%m-%d %H:%M")
        screening_date_objects.append(
            ScreeningDate(
                date=parsed_screening_date.date(),
                time=str(parsed_screening_date.time())[0:5],
            )
        )
    return screening_date_objects


def download_image_from_url(image_url) -> Tuple[Optional[BytesIO], Optional[str]]:
    if image_url is None:
        return None, None
    file_extension = image_url.split(".")[-1]
    file_name = (
        hashlib.md5(image_url.encode("utf-8")).hexdigest() + "." + file_extension
    )

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    r = session.get(image_url)
    if r.ok is False:
        return None, None

    image_bytes = BytesIO(r.content)

    # test that the return is a valid image
    try:
        Image.open(image_bytes)
        image_bytes.seek(0)
    except UnidentifiedImageError:
        return None, None
    return image_bytes, file_name


def get_img_filename_from_url(image_url) -> str:
    file_extension = image_url.split(".")[-1]
    return secure_filename(
        hashlib.md5(image_url.encode("utf-8")).hexdigest() + "." + file_extension
    )


def get_img_path_from_filename(file_name, app) -> Optional[str]:
    """returns image path if image from given url already exists locally,
    None otherwise"""
    img_path = os.path.join(app.config.get("UPLOAD_FOLDER"), file_name)
    if os.path.exists(img_path):
        return img_path
    return None


def get_image_metadata(img_path):
    with open(img_path, "rb") as f:
        loaded_image = Image.open(f)
    return loaded_image.width, loaded_image.height


def _build_feature_description(scrapped_feature: ScrappedFeature) -> str:
    """Extracts the responsibility for constructing the movie description string"""
    description_parts = []
    if scrapped_feature.original_title:
        description_parts.append(scrapped_feature.original_title.strip())
    if scrapped_feature.price:
        description_parts.append(scrapped_feature.price)
    if scrapped_feature.director:
        description_parts.append(scrapped_feature.director)
    if scrapped_feature.classification:
        description_parts.append(scrapped_feature.classification)
    if scrapped_feature.general_info:
        description_parts.append(scrapped_feature.general_info)
    if scrapped_feature.excerpt:
        description_parts.append(scrapped_feature.excerpt)
        
    return "\n".join(description_parts).strip()


def _handle_poster_upload(poster_url: Optional[str], current_app) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    """Extracts the responsibility for downloading and saving the movie poster"""
    if not poster_url:
        return None, None, None
        
    img, filename = download_image_from_url(poster_url)
    if img is not None:
        return save_image(img, current_app, filename)
        
    return None, None, None


def _resolve_screening_dates(cinema_slug: str, screening, scrapped_dates: List[ScreeningDate]) -> List[ScreeningDate]:
    """Extracts the complex logic for merging dates, including the Capitolio rule"""
    if cinema_slug == "capitolio":
        # Capitólio Strategy: deletes records from the day and relies on the new ones (Issue #163)
        received_dates_for_screening = [sd.date for sd in scrapped_dates]
        existing_dates = build_dates(
            [
                f"{sd.date}T{sd.time}"
                for sd in screening.dates
                if sd.date not in received_dates_for_screening
            ]
        )
    else:
        # Standard Strategy for other cinemas
        existing_dates = build_dates(
            [f"{sd.date}T{sd.time}" for sd in screening.dates]
        )

    # Appends the new dates, avoiding exact duplicates of day and time
    for new_date in scrapped_dates:
        already_registered = any(
            existing_date.date == new_date.date and existing_date.time == new_date.time
            for existing_date in existing_dates
        )
        if not already_registered:
            existing_dates.append(new_date)
            
    return existing_dates


def import_scrapped_results(scrapped_results: ScrappedResult, current_app) -> int:
    """Extracts the main logic for importing scrapped results: now acts only as an orchestrator"""
    created_features = 0
    
    for scrapped_cinema in scrapped_results.cinemas:
        cinema = get_cinema_by_slug(scrapped_cinema.slug)
        
        for scrapped_feature in scrapped_cinema.features:
            movie = get_movie_by_title_or_create(scrapped_feature.title)
            
            # 1. Processes scraping dates
            screenings_dates = (
                build_dates(scrapped_feature.time) 
                if scrapped_feature.time 
                else build_dates([datetime.now().strftime("%Y-%m-%dT%H:%M")])
            )
            
            # 2. Searches for existing screening
            screening = get_screening_by_movie_id_and_cinema_id(movie.id, cinema.id)
            
            if not screening:
                # 3. Creates new screening (Scenario A)
                description = _build_feature_description(scrapped_feature)
                img_filename, img_width, img_height = _handle_poster_upload(scrapped_feature.poster, current_app)
                
                create_screening(
                    movie_id=movie.id,
                    description=description,
                    cinema_id=cinema.id,
                    screening_dates=screenings_dates,
                    image=img_filename,
                    image_width=img_width,
                    image_height=img_height,
                    is_draft=False,
                    image_alt=None,
                    url_origin=scrapped_feature.read_more,
                )
            else:
                # 4. Updates existing screening (Scenario B)
                updated_dates = _resolve_screening_dates(cinema.slug, screening, screenings_dates)
                update_screening_dates(screening, updated_dates)
                
            created_features += 1
            
    return created_features