describe('Teste 1 - Visualização da programação do dia (Público)', () => {
  
  // Visita a página inicial
  beforeEach(() => {
    cy.visit('http://localhost:5000');
  });

  it('Cenário 1: Deve permitir que um visitante veja os cinemas e a programação sem rascunhos', () => {
    // Verifica se os links ou badges dos cinemas principais estão visíveis na tela
    cy.get('a[href*="#capitolio"]').should('be.visible');
    cy.get('a[href*="#sala-redencao"]').should('be.visible');

    // Garante que o texto explicativo de boas-vindas carregou com o nome de um cinema
    cy.get('.alert-link').should('contain.text', 'Cinemateca Capitólio');
  });
});