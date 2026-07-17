# Relatório de Refatoração e Padrões de Projeto

Este documento detalha as intervenções realizadas no código para eliminar code smells, aumentar a manutenibilidade e alinhar a arquitetura aos princípios SOLID e Padrões de Projeto.

# Code Smells Identificados

## 1. Long Method
- **Trecho do Código:** Função `import_scrapped_results` no ecossistema de processamento de dados (103 linhas originais).
- **Problema Identificado:** O método acumulava múltiplas responsabilidades, violando o Princípio de Responsabilidade Única (SRP). Ele realizava simultaneamente a iteração de dados, formatação de strings, gerenciamento de downloads de imagens, regras de negócio específicas para cinemas e validação de datas.  
- **Solução Aplicada:** Aplicação da técnica Extract Method (Extração de Método), dividindo o bloco monolítico em métodos privados especialistas. 
- **Justificativa Técnica:** A função original foi decomposta em métodos menores e especialistas:  
* `_build_feature_description()`: Formatação de descrição.  
* `_handle_poster_upload()`: Gestão de arquivos de imagem.  
* `_resolve_screening_dates()`: Lógica de datas.  
*Benefícios:* A função principal tornou-se uma orquestradora de alto nível, facilitando a leitura e os testes unitários, tendo 48 linhas.

**Alterações:**
  ```Python
  def _build_feature_description(scrapped_feature: ScrappedFeature) -> str:
    """Extrai a responsabilidade de montar a string de descrição do filme"""
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
```
 ```Python
def _handle_poster_upload(poster_url: Optional[str], current_app) -> Tuple[Optional[str], Optional[int], Optional[int]]:
    """Extrai a responsabilidade de baixar e salvar o poster do filme"""
    if not poster_url:
        return None, None, None
        
    img, filename = download_image_from_url(poster_url)
    if img is not None:
        return save_image(img, current_app, filename)
        
    return None, None, None

```
 ```Python
def _resolve_screening_dates(cinema_slug: str, screening, scrapped_dates: List[ScreeningDate]) -> List[ScreeningDate]:
    """Extrai a lógica complexa de merge de datas, incluindo a regra do Capitólio"""
    if cinema_slug == "capitolio":
        # Estratégia do Capitólio: deleta registros do dia e confia nos novos (Issue #163)
        received_dates_for_screening = [sd.date for sd in scrapped_dates]
        existing_dates = build_dates(
            [
                f"{sd.date}T{sd.time}"
                for sd in screening.dates
                if sd.date not in received_dates_for_screening
            ]
        )
    else:
        # Estratégia padrão para os demais cinemas
        existing_dates = build_dates(
            [f"{sd.date}T{sd.time}" for sd in screening.dates]
        )

    # Faz o append das novas datas evitando duplicatas exatas de dia e horário
    for new_date in scrapped_dates:
        already_registered = any(
            existing_date.date == new_date.date and existing_date.time == new_date.time
            for existing_date in existing_dates
        )
        if not already_registered:
            existing_dates.append(new_date)
            
    return existing_dates

```
 ```Python
def import_scrapped_results(scrapped_results: ScrappedResult, current_app) -> int:
    """Função principal refatorada: agora atua apenas como uma Orquestradora"""
    created_features = 0
    
    for scrapped_cinema in scrapped_results.cinemas:
        cinema = get_cinema_by_slug(scrapped_cinema.slug)
        
        for scrapped_feature in scrapped_cinema.features:
            movie = get_movie_by_title_or_create(scrapped_feature.title)
            
            # Processa datas da raspagem
            screenings_dates = (
                build_dates(scrapped_feature.time) 
                if scrapped_feature.time 
                else build_dates([datetime.now().strftime("%Y-%m-%dT%H:%M")])
            )
            
            # Busca exibição existente
            screening = get_screening_by_movie_id_and_cinema_id(movie.id, cinema.id)
            
            if not screening:
                # 3. Criação de nova exibição (Cenário A)
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
                # Atualização de exibição existente
                updated_dates = _resolve_screening_dates(cinema.slug, screening, screenings_dates)
                update_screening_dates(screening, updated_dates)
                
            created_features += 1
            
    return created_features
  ```



## 2. Switch Statement
- **Trecho do Código:** Bloco condicional estruturado com checagens em string rígidas, como `if cinema.slug == "capitolio"`, dentro do fluxo de processamento e parsing de datas das sessões. 
- **Problema Identificado:** O uso de condicionais baseadas em strings para definir comportamentos específicos. Isso viola o Princípio Aberto-Fechado, pois a adição de um novo cinema com regras próprias exigiria a alteração do código existente.  
- **Solução Aplicada:** Substituição da estrutura condiciona através do padrão de projeto Strategy. 
- **Justificativa Técnica:** Foi criada uma interface abstrata `ScreeningDateStrategy` e implementações concretas (`DefaultScreeningDateStrategy` e `CapitolioScreeningDateStrategy`). Um dicionário de mapeamento (`STRATEGY_MAP`) permite a busca dinâmica da estratégia correta sem condicionais rígidas.  
*Benefícios:* O sistema tornou-se extensível. Novos comportamentos de cinemas podem ser adicionados criando novas classes, sem risco de quebrar o fluxo principal.

```Python
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
```
**Alterações:**
```Python
# Strategy Interface Definition
class ScreeningDateStrategy(ABC):
    @abstractmethod
    def resolve(self, screening, scrapped_dates: List[ScreeningDate]) -> List[ScreeningDate]:
        """Abstract contract definindo como resolver as datas de exibição"""
        pass
# Estratégia padrão para a maioria dos cinemas
class DefaultScreeningDateStrategy(ScreeningDateStrategy):
    def resolve(self, screening, scrapped_dates: List[ScreeningDate]) -> List[ScreeningDate]:
        # creates new instances to prevent memory reference errors
        return build_dates([f"{sd.date}T{sd.time}" for sd in screening.dates])


# Specialized Strategy for Cinema Capitólio (Issue #163)
class CapitolioScreeningDateStrategy(ScreeningDateStrategy):
    def resolve(self, screening, scrapped_dates: List[ScreeningDate]) -> List[ScreeningDate]:
        # Capitólio specific logic: deletes records for the day and relies on the new ones
        received_dates_for_screening = [sd.date for sd in scrapped_dates]
        return build_dates([
            f"{sd.date}T{sd.time}"
            for sd in screening.dates
            if sd.date not in received_dates_for_screening
        ])


# Dicionário de mapeamento (elimina if/else)
STRATEGY_MAP = {
    "capitolio": CapitolioScreeningDateStrategy()
}


def _resolve_screening_dates(cinema_slug: str, screening, scrapped_dates: List[ScreeningDate]) -> List[ScreeningDate]:
    """
   Refatorado: Substituímos a complexidade condicional pelo padrão Strategy.
  Agora, a estratégia correta é recuperada de forma transparente com base no slug do cinema.
    """
    # se o cinema tiver uma estratégia definida, utilize-a; caso contrário, utilize a estratégia padrão.
    strategy = STRATEGY_MAP.get(cinema_slug, DefaultScreeningDateStrategy())
    
    # executa o comportamento polimórfico sem que o método precise saber com qual cinema está lidando.
    existing_dates = strategy.resolve(screening, scrapped_dates)

    # mantém a lógica final de mesclagem e evita duplicatas exatas.
    for new_date in scrapped_dates:
        already_registered = any(
            existing_date.date == new_date.date and existing_date.time == new_date.time
```


## 3. Feature Envy
- **Trecho do Código** Funções `runScrap()` e `import_screenings()` no arquivo de rotas `screening.py`.  
- **Problema Identificado:** As rotas acessavam diretamente a estrutura interna e aninhada do objeto `Runner` (`runner.scrapped_results.cinemas`) para realizar validações. Segundo Martin Fowler, isso ocorre quando um método se interessa mais pelos dados de outra classe do que daquela onde reside, gerando acoplamento inadequado.  
- **Solução Aplicada:** Encapsulamento da lógica externa injetando o padrão de projeto Visitor, limpando o fluxo das rotas.  
- **Justificativa Técnica:** Foi implementado o mecanismo de *Double Dispatch*, onde a classe `Runner` aceita um visitante (`accept(visitor)`). Foi criado o `CinemaValidationVisitor` para encapsular a lógica de validação que antes "poluía" a rota.  
_Benefícios:_ As rotas foram desacopladas da estrutura interna do `Runner`. Agora, a rota apenas coordena a execução, delegando a lógica de processamento interna ao visitante especialista.

```Python
for json_cinema in runner.scrapped_results.cinemas:
    cinema = get_cinema_by_slug(json_cinema.slug)
    if cinema is None:
        flash(f"Sala {json_cinema.slug} não encontrada.")
        return render_template("screening/import.html", suggestions=[])
```
**Alterações:** routes/screening.py
```Python
class CinemaValidationVisitor(RunnerVisitor):
    def __init__(self):
        self.is_valid = True
        self.invalid_cinema_slug = None

    def visit_runner(self, runner) -> None:
        # Toda a lógica que antes causava Feature Envy na rota agora roda aqui dentro
        for json_cinema in runner.scrapped_results.cinemas:
            cinema = get_cinema_by_slug(json_cinema.slug)
            if cinema is None:
                self.is_valid = False
                self.invalid_cinema_slug = json_cinema.slug
                return 
```
**Alterações:** service/runner.py
```Python
def accept(self, visitor):
        """ Permite que um visitante acesse a estrutura interna do Runner """
        visitor.visit_runner(self)
```


# Padrões de Projeto Aplicados

## Padrão 1: Strategy
  - **Onde foi aplicado:** Na resolução de regras de datas específicas por cinema dentro do fluxo de importação. Foi criada uma interface abstrata `ScreeningDateStrategy` e suas implementações concretas: `DefaultScreeningDateStrategy` e `CapitolioScreeningDateStrategy`, gerenciadas dinamicamente por um mapa de inicialização `(STRATEGY_MAP)`.
  - **Justificativa:** Isolar os algoritmos variáveis de tratamento de datas de modo que fiquem independentes do fluxo principal. Isso permite que o sistema seja extensível: novos cinemas com comportamentos complexos de datas podem ser acoplados criando apenas uma nova classe, sem risco de quebra ou necessidade de alterar o código que já funciona.

## Padrão 2: Visitor
  - **Onde foi aplicado:** No desacoplamento entre as rotas HTTP em `screening.py` e a árvore de dados do componente Runner. Foi criado o `CinemaValidationVisitor` e adicionado o método `accept(visitor)` dentro da estrutura do Runner.
  - **Justificativa:** Limpar a responsabilidade da camada de rotas (que deve apenas orquestrar requisições e respostas) e impedir que ela precise conhecer a fundo as estruturas de dados do motor de raspagem. Toda a lógica complexa de validação interna foi movida para o visitante especialista, reduzindo drasticamente o acoplamento entre as classes.
