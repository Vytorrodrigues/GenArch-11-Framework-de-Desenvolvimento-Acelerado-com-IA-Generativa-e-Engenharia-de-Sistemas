# Requisito funcionais

- RF01: O sistema deve permitir a inserção de um conteúdo de texto.
- RF02: O sistema deve permitir a configuração do tamanho da fonte.
- RF03: O sistema deve permitir a escolha da cor da fonte entre cinco opções (preto, branco, azul, amarelo, cinza).
- RF04: O sistema deve permitir a escolha da cor de fundo entre cinco opções (preto, branco, azul, amarelo, cinza).
- RF05: O sistema deve permitir ao usuário selecionar o componente de destino (Label, Edit ou Memo).
- RF06: O sistema deve validar se as cores escolhidas estão dentro da paleta permitida.

# Requisitos não funcionais

- RNF01 (Independência de Plataforma): A classe não deve herdar de classes visuais específicas de frameworks, deve manter o foco conceitual
- RNF02 (Restrição de Domínio): As cores devem ser limitadas estritamente aos tons: preto, branco, azul, amarelo e cinza.
- RNF03 (Usabilidade): Os componentes de exibição permitidos devem ser restritos exclusivamente a label, edit e memo
- RNF04 (Extensibilidade): A estrutura deve permitir que novos tipos de componentes sejam adicionados futuramente sem quebrar a lógica de atributos.