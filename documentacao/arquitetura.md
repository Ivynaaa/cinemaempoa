<img width="3241" height="717" alt="image" src="https://github.com/user-attachments/assets/b6ca9562-c319-4fd7-a33e-53cd1e6cce3c" />

O código em uml:
@startuml
skinparam componentStyle uml2
skinparam packageStyle rectangle

package "cinemaempoa.main" {
  component "cinemaempoa.py\nCLI Scraper Runner" as CLI
  component "utils.py\nJSON / utilitários" as Utils
  package "scrapers" {
    component "llms.py" as ScraperLLM
    component "imdb.py" as ScraperIMDb
    component "capitolio.py" as ScraperCapitolio
    component "cinebancarios.py" as ScraperCineBancarios
    component "paulo_amorim.py" as ScraperPauloAmorim
    component "sala_redencao.py" as ScraperSalaRedencao
  }
}

package "flask_backend" {
  component "create_app\nApp Factory" as AppFactory
  component "env_config.py\nConfig de ambiente" as EnvConfig
  component "db.py\nDB Session + CLI" as DB
  component "models.py\nORM Models" as Models
  component "import_json.py\nScraped DTOs" as ImportJson

  package "repository" {
    component "movies.py" as RepoMovies
    component "screenings.py" as RepoScreenings
    component "cinemas.py" as RepoCinemas
    component "users.py" as RepoUsers
    component "blog_posts.py" as RepoBlogPosts
    component "poster_fetch_attempts.py" as RepoPosterFetchAttempts
  }

  package "routes" {
    component "auth.py" as RouteAuth
    component "screening.py" as RouteScreening
    component "movie.py" as RouteMovie
    component "blog.py" as RouteBlog
    component "page.py" as RoutePage
    package "admin" {
      component "blog.py" as RouteAdminBlog
    }
  }

  package "service" {
    component "screening.py" as ServiceScreening
    component "upload.py" as ServiceUpload
    component "poster_pipeline.py" as ServicePosterPipeline
    component "tmdb.py" as ServiceTmdb
    component "gemini_api.py" as ServiceGemini
    component "runner.py" as ServiceRunner
    component "shared.py" as ServiceShared
  }

  package "seeds" {
    component "cinema_seeds.py" as SeedCinema
    component "movie_seeds.py" as SeedMovie
    component "screening_seeds.py" as SeedScreening
    component "user_seeds.py" as SeedUser
  }

  package "routes/templates" {
    component "templates/*.html" as Templates
  }
}

component "Database\n(SQLAlchemy / Alembic)" as Database
component "External Services\n(imgBB, TMDB, IMDb, Gemini)" as ExternalAPIs
component "Browser / Client" as Client

CLI --> ScraperCapitolio
CLI --> ScraperCineBancarios
CLI --> ScraperPauloAmorim
CLI --> ScraperSalaRedencao
CLI --> Utils

AppFactory --> DB
AppFactory --> EnvConfig
AppFactory --> Routes
AppFactory --> Templates

RouteAuth --> RepoUsers
RouteScreening --> RepoCinemas
RouteScreening --> RepoScreenings
RouteScreening --> RepoMovies
RouteScreening --> ServiceScreening
RouteScreening --> RouteAuth

RouteMovie --> RepoMovies
RouteMovie --> RepoScreenings
RouteMovie --> RouteAuth

RouteBlog --> RepoBlogPosts
RoutePage --> RepoCinemas

RouteAdminBlog --> RepoBlogPosts
RouteAdminBlog --> RouteAuth

ServiceScreening --> ServiceUpload
ServiceScreening --> ServiceTmdb
ServiceScreening --> ServiceGemini
ServiceScreening --> RepoCinemas
ServiceScreening --> RepoMovies
ServiceScreening --> RepoScreenings

ServiceUpload --> ExternalAPIs
ServicePosterPipeline --> ServiceTmdb
ServicePosterPipeline --> ServiceUpload
ServiceRunner --> ServiceScreening
ServiceRunner --> ServiceShared

DB --> Models
RepoMovies --> DB
RepoScreenings --> DB
RepoCinemas --> DB
RepoUsers --> DB
RepoBlogPosts --> DB
RepoPosterFetchAttempts --> DB


RepoMovies --> Models
/'
RepoScreenings --> Models
RepoCinemas --> Models
RepoUsers --> Models
RepoBlogPosts --> Models
RepoPosterFetchAttempts --> Models
'/

DB --> Database
AppFactory --> Database
/'
RepoMovies --> Database
RepoScreenings --> Database
RepoCinemas --> Database
'/
RepoUsers --> Database
/'
RepoBlogPosts --> Database
RepoPosterFetchAttempts --> Database
'/

@enduml


 ## Arquitetura
  A arquitetura desse projeto tenta ser um MVC Web mas acaba sendo um "Bom Big Ball of Mud" com certa desorganização, você pode ver o screening.py de services em flask_backend como exemplo, além de ter o mesmo nome de outra classe(screening.py de routes), ela aponta para qualquer lugar no backend, no diagrama UML ainda está faltando alegar o uso de models, e de alguns 3rd party, mas pelo nome você consegue "achar" o que precisa dele, ele obviamente por exemplo vai usar o model Screening já que ele é chamado screening, e ele vai ter requisitos similares aos outros screenings, por isso ser um "Bom Big Ball of Mud", mas qualquer mudança pode ser atrasada e dificultada pela arquitetura complicada
