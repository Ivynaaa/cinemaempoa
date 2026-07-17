# Contribuições

- Gustavo Rodrigues de Oliveira
- Ivyna Alves Santos Magalhães

---

## Caminho A: Manutenção Evolutiva/Corretiva

- **Link da Issue Escolhida:** [Adicionar uma tag com o cinema junto ao filme
 #211](https://github.com/cumbucadev/cinemaempoa/issues/211)
- **Descrição da Solução:** 
  - Para resolver o problema de identificação do cinema na página inicial em dispositivos móveis, foi realizada uma refatoração para reaproveitar as tags visuais (badges) de maneira global e independente.
  - O dicionário COLORS (que mapeia os slugs dos cinemas para suas respectivas cores hexadecimais) foi movido para fora do escopo da função *programacao()*.
  - Com essa mudança de escopo as cores agora podem ser importadas ou injetadas diretamente no contexto de outras rotas do sistema, eliminando a dependência estrita de uma única rota para estilizar as tags. 

----

## Caminho B: Engenharia de Qualidade e Refatoração

- **Descrição da Refatoração:**
- Implementamos uma refatoração focada na redução de acoplamento, aplicação dos princípios SOLID (especialmente SRP e OCP) e no aumento da extensibilidade do processamento de dados e rotas.
- Foram tratados Code Smells críticos como *Long Method*, *Switch Statement* e *Feature Envy*. A lógicade importação de sessões, tratamento de regras específicas de cinemas e validações de rotas foi extraída e descentralizada para componentes especializados.
- Introduzidos automação dos testes de aceitação E2E utilizando o Cypress. Foram mapeados e cobertos os 3 cenários principais da regra de negócio do sistema.
- Aproveitamento da suíte de testes em Python que já existente no diretório cinemaempoa/tests foi criado um fluxo automatizado utilizando o GitHub Actions.
---

## Lista de Pull Requests Criados

1. **[PR1 - Arquitetura](https://github.com/Ivynaaa/cinemaempoa/pull/2) :** Análise e representação a arquitetura do sistema.
2. **[PR2 - Padrões e Refatoração](https://github.com/Ivynaaa/cinemaempoa/pull/5) :** Relatório analítico dos *Code Smells* identificados e dos Padrões de Projeto aplicados.
3. **[PR3 - Testes](https://github.com/Ivynaaa/cinemaempoa/pull/6) :** Implementação dos Testes de Aceitação Automatizados.
5. **[PR5 - DevOps](https://github.com/Ivynaaa/cinemaempoa/pull/7) :** Implementação do fluxo de testes automatizado utilizando o GitHub Actions.
6. **[PR6 - Issue Resolvida](https://github.com/cumbucadev/cinemaempoa/pull/213) :** Resolução da issue no repositório original.

## Papel de Cada Integrante

- **Gustavo:**
  - Arquitetura e Modelagem: Responsável pela análise técnica e representação visual da arquitetura do sistema.
  - DevOps & CI/CD: Implementou a automação dos testes existentes integrando o pipeline de Integração Contínua via GitHub Actions.
  - Caminho A (Manutenção Evolutiva/Corretiva): Refatorou o frontend (index.html) para herdar e reaproveitar as tags visuais (badges) de forma responsiva na página inicial.
- **Ivyna:**
  - Manutenção Evolutiva/Corretiva (Caminho A): Refatorou o escopo do dicionário COLORS no backend (screening.py), tornando o mapeamento de cores global e acessível para qualquer rota estilizar as tags de forma dinâmica.
  - Padrões de Projeto e Refatoração (Caminho B): Identificou e mitigou os code smells (Long Method, Switch Statement e Feature Envy) aplicando os padrões Strategy, Visitor.
  - Testes de Software: Desenvolveu a suíte de testes de aceitação com Cypress, mapeando e cobrindo os 3 fluxos de negócio do sistema.

