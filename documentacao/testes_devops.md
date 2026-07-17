# Cenários de Testes Automatizados

- Cenários de testes automatizados implementados com Cypress.

## Cenário 1: Visualização da Programação do Dia (Público)

```gherkin
Dado que o usuário acessa a página inicial do Cinema em POA
Quando a página carregar completamente
Então o sistema deve exibir a grade de filmes programados para o dia atual
E cada filme deve exibir visivelmente a tag colorida do seu respectivo cinema
Mas nenhum filme marcado com o status "Rascunho" deve ser exibido na listagem
```
- **O que o teste cobre:** Garante que a experiência do usuário final (visitante) esteja íntegra. Valida a renderização dinâmica da programação real do dia, a presença visual das novas badges de cinema (com as cores corretas extraídas globalmente de screening.py) e atua como uma barreira de segurança para assegurar que conteúdos de Rascunhos permaneçam ocultos para o público.

 ## Cenário 2: Autenticação e Criação de Nova Sessão de Filme (Admin)

```gherkin
Dado que o usuário está na tela de login administrativo
Quando ele insere credenciais válidas e submete o formulário
Então o sistema concede acesso ao painel de controle
Quando o administrador acessa o formulário de cadastro de sessões
E preenche as informações com uma data futura, faz o upload real de um pôster e salva
Então o sistema deve exibir uma mensagem de sucesso
E a nova sessão deve constar na base de dados
```
- **O que o teste cobre:** Cobre o fluxo crítico de autenticação do sistema de gerenciamento. Valida o fluxo de persistência de dados manual por parte do administrador, testando o tratamento de inputs com datas dinâmicas, o processamento de multipart/form-data (upload físico de arquivos de imagem/pôster) e o comportamento dos alertas de sucesso da interface.

 ## Cenário 3: Importação de Sessões via Scraping Automático (Admin)

 ```gherkin
Dado que o administrador está autenticado no painel de controle
Quando ele acessa a área de integração e seleciona múltiplos cinemas para atualizar
E dispara o comando de importação automática por raspagem de dados
Então o sistema deve iniciar as tarefas assíncronas em segundo plano
E o teste deve monitorar e tolerar o tempo de resposta do robô (polling/timeout assíncrono)
Ao final do processo, a interface deve atualizar o status para sucesso
```
- **O que o teste cobre:** Valida a integração entre a interface do painel administrativo e o motor de raspagem de dados (Runner). Como o processo de scraping depende de requisições externas e leva tempo, o teste cobre especificamente a robustez assíncrona do frontend, garantindo que o sistema trate corretamente tempos de espera estendidos (timeouts) sem travar a sessão do usuário.

# Execução dos testes

Instalar dependências:

```bash
npm install
```

Executar Cypress:

```bash
npx cypress open
```
Ou para executar no terminal:

```bash
npx cypress run
```

# DevOps e Integração Contínua (CI)

- **Abordagem e Implementação**
  - Configuramos uma esteira de automação utilizando o GitHub Actions para acionar a suíte de testes já existente localizada em `cinemaempoa/tests`.
  - Como o comando para rodar essas validações já estava previamente criado e descrito no `README.md` do programa, o esforço concentrou-se em criar o arquivo de workflow `(tests.yml)` para fazer com que o GitHub Actions execute automaticamente esses mesmos testes sempre que um Pull Request (PR) for aberto ou atualizado.
























