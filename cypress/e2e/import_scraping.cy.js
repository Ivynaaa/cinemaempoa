describe('Teste 3 - Importação de Sessões (Admin)', () => {

   // Limpeza dos cookies e a sessão para garantir um estado limpo
  beforeEach(() => {
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  it('Cenário 3: Importação de Sessões com scraping', () => {
    // Vai para a página de login e se autentica
    cy.visit('http://localhost:5000/auth/login'); 
    cy.get('input[name="username"]').type('cinemaempoa'); 
    cy.get('input[name="password"]').type('123123');
    cy.get('form').submit();

    // Navega até a página de importação de sessões
    cy.visit('http://localhost:5000/screening/import');

    // Seleciona os cinemas para os quais deseja importar as sessões
    cy.contains('Cinemateca Paulo Amorim').click();

    // Clica no botão para disparar o scraping automático
    cy.get('button, input[type="submit"], a')
      .contains('Fazer scrapping dos cinemas selecionados')
      .click();

    // Scraping fazem requisições externas para sites reais
    // o cypress espera 20 segundos pela resposta do backend sem derrubar o teste por lentidão
    cy.url({ timeout: 20000 }).should('include', '/screening/import');

    // Valida as sessões criadas
    cy.get('.alert-success', { timeout: 20000 })
      .should('be.visible')
      .and('contain.text', 'sessões criadas com sucesso!')
      .visit('http://localhost:5000/program'); 
  });
});