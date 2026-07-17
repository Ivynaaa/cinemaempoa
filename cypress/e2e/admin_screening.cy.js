describe('Teste 2 - Autenticação e Criação de Nova Sessão de Filme (Admin)', () => {

  // Limpeza dos cookies e a sessão para garantir um estado limpo
  beforeEach(() => {
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  it('Cenário 2: Efetuar login e cadastrar uma nova sessão de filme', () => {
    // Vai para a página de login e se autentica
    cy.visit('http://localhost:5000/auth/login'); 
    cy.get('input[name="username"]').type('cinemaempoa'); 
    cy.get('input[name="password"]').type('123123');
    cy.get('form').submit();

    // Vai para o formulário de criação de sessão
    cy.visit('http://localhost:5000/screening/new');

     // Seleciona o primeiro cinema do select preenche a data
    cy.get('select[name="cinema_id"]').select('1'); 
    cy.get('input[name="screening_dates"]').type('2026-07-16T19:30');

    // Preenche os campos
    cy.get('input[name="movie_title"]').type('Morto Não Fala');
    cy.get('[name="image_alt"]').type('Poster do filme Morto Não Fala');
    cy.get('input[name="movie_poster"]').selectFile('cypress/fixtures/poster_teste.jpg');
    cy.get('textarea[name="description"]').type('Exibição do Teste 2 - Filme Morto Não Fala');
    
    // Define o status da sessão como ativa
    cy.get(':nth-child(3) > [name="status"]').click();

    // Submete o formulário
    cy.get('form').submit();

    cy.visit('http://localhost:5000/auth/login'); 
    cy.get('input[name="username"]').type('cinemaempoa'); 
    cy.get('input[name="password"]').type('123123');
    cy.get('form').submit();

    // Vai para o formulário de criação de sessão Rascunho
    cy.visit('http://localhost:5000/screening/new');
    cy.get('select[name="cinema_id"]').select('1'); 
    cy.get('input[name="screening_dates"]').type('2026-07-16T19:30');
    cy.get('input[name="movie_title"]').type('Morto Não Fala');
    cy.get('[name="image_alt"]').type('Poster do filme Morto Não Fala');
    cy.get('input[name="movie_poster"]').selectFile('cypress/fixtures/poster_teste.jpg');
    cy.get('textarea[name="description"]').type('Exibição do Teste 2 Rascunho - Filme Morto Não Fala');
    cy.get(':nth-child(2) > [name="status"]').click();
    cy.get('form').submit();

    // Valida se a sessão foi criada com sucesso
    cy.url().should('eq', 'http://localhost:5000/');
    cy.get('.alert-success').should('be.visible')
      .and('contain.text', 'Sessão «Morto Não Fala» criada com sucesso!');
  });
});