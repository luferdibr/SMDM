# Regras de Negocio do SMDM

Este arquivo centraliza regras funcionais do sistema. Ele deve ser atualizado a cada nova rotina, tabela ou regra validada.

## Seguranca, Usuario, Perfil e Menu

- ROOT e o perfil de maior autoridade do sistema. Deve existir apenas um ROOT.
- ROOT pode executar todas as rotinas e administrar todos os usuarios, perfis, menus e permissoes.
- A recuperacao da senha ROOT so pode ocorrer no computador servidor e deve gerar arquivo TXT na pasta onde esta o banco de dados.
- ADMIN pode gerenciar usuarios, perfis e Perfil x Menu, respeitando niveis de acesso.
- ADMIN pode editar outros ADMIN.
- ADMIN nao pode administrar ROOT.
- ADMIN nao pode desabilitar ou excluir o ultimo ADMIN ativo; somente ROOT pode fazer isso.
- Somente ROOT pode editar o cadastro estrutural de Menu.
- Usuario inativo ou perfil inativo deve ter acesso apenas a Logout.
- O menu deve ser recarregado da tabela sempre que o usuario retornar ao menu.
- O menu e montado por perfil usando a tabela PerfilMenu.
- A hierarquia do menu usa T como agrupador pai, M como grupo intermediario e S como item executavel.
- Ao entrar em uma opcao executavel S, o menu fecha para liberar area de trabalho. Ao sair da rotina, a tela limpa, o menu expande e e recarregado conforme o perfil atual.
- Se S apontar para uma rotina inexistente, deve aparecer a mensagem: "item em producao, aguarde!".
- Apos 3 erros de senha, o usuario deve aguardar 5 minutos. A cada novo bloco de 3 erros, acrescenta mais 5 minutos.
- ROOT nao sofre bloqueio por tentativas de senha.
- A senha ROOT e digitada na instalacao e nao exige troca no primeiro acesso.
- O ADMIN inicial exige troca de senha no primeiro acesso.
- Usuarios novos recebem a senha inicial do ADMIN e devem trocar no primeiro acesso.

## Instalacao e Dados Iniciais

- Na inicializacao, o sistema valida a estrutura antes do login.
- A rotina de instalacao verifica tabelas, colunas, menus e dados iniciais necessarios.
- Cada nova tela de cadastro deve ter sua tabela equivalente criada ou evoluida no install_service.py.
- Registros iniciais devem ficar preferencialmente em config/initial_data.json ou arquivo de configuracao equivalente.
- A rotina de instalacao muda conforme novas rotinas e tabelas forem implantadas.

## Regras Gerais de Cadastramento

- O SMDM deve priorizar o uso em desktops por administradores, equipe interna e equipe de desenvolvimento.
- As telas desktop devem ser praticas, objetivas e orientadas a produtividade, com menor uso de elementos graficos.
- Campos editaveis devem usar layout compacto, bem distribuido e organizado por secoes, abas ou grupos logicos.
- Campos mais usados devem ficar visiveis na primeira area da tela, evitando rolagem excessiva.
- As telas devem permitir operacao eficiente por teclado, incluindo Tab, Enter, atalhos e foco inicial correto.
- Listagens devem permitir busca, filtros, ordenacao e abertura rapida do registro.
- Campos obrigatorios, opcionais, calculados e somente leitura devem ser claramente diferenciados.
- Mensagens de validacao devem ser diretas e proximas do campo com problema.
- Todo cadastro principal deve possuir identificador unico interno.
- Todo cadastro principal deve possuir status, preferencialmente ATIVO ou INATIVO.
- Registros usados em historico, orcamento, evento, contrato, financeiro, calendario ou movimentacao nao devem ser excluidos fisicamente.
- A regra padrao deve ser inativacao, nao exclusao fisica.
- Registros inativos nao devem aparecer como opcao padrao em novos lancamentos, mas devem aparecer em consultas historicas.
- Todo cadastro deve registrar data de criacao, usuario criador, data da ultima alteracao e usuario da ultima alteracao.
- Campos obrigatorios devem ser validados antes de salvar.
- O sistema deve impedir duplicidade em campos criticos, como CPF, CNPJ, e-mail principal, nome de sede, nome de figurino ou codigo interno, conforme o tipo de cadastro.
- Alteracoes em dados sensiveis devem ser preparadas para auditoria em fase futura.

## Enderecos

- Cadastros com endereco devem seguir campos padronizados: CEP, Logradouro, Numero, Complemento, Bairro, Municipio, UF, Pais, Latitude, Longitude, FonteGeo, DataGeo e GeoStatus quando aplicavel.
- O pais padrao deve ser Brasil.
- Para enderecos brasileiros, Municipio e UF devem ser obrigatorios quando o endereco for informado.
- CEP deve ser validado quando informado, mas o sistema deve permitir endereco sem CEP quando logradouro, municipio e UF forem suficientes.
- A edicao assistida de endereco deve usar rotina padrao reutilizavel nos cadastros.
- A validacao de CEP deve considerar cache local de pesquisas antes de qualquer consulta online.
- O cache local dos enderecos mais utilizados deve ser controlado principalmente pelo CEP.
- Ao informar CEP, o sistema deve normalizar o CEP, consultar primeiro o cache local e preencher logradouro, bairro, municipio, UF e pais quando houver retorno.
- Se o CEP existir no cache local e estiver ativo/valido, o sistema nao deve consultar a web.
- Se o CEP nao existir no cache, estiver inativo ou estiver vencido, o sistema pode consultar servico externo.
- Toda consulta online de CEP/endereco bem-sucedida deve gravar ou atualizar o cache local para reduzir consultas repetidas.
- O cache de CEP deve registrar data da consulta, data do ultimo uso e quantidade de uso.
- O cache de CEP pode descartar ou marcar como vencidas consultas antigas com mais de 3 a 6 meses.
- Na falta de CEP, o usuario deve poder informar endereco, cidade e UF para pesquisar e escolher um resultado.
- Enderecos brasileiros, especialmente do RS, sao predominantes, mas o modelo deve aceitar poucos estrangeiros.
- A localizacao geografica deve ser gerada apos a montagem do endereco, usando geocodificacao por Nominatim/geopy ou servico equivalente quando acionada pelo usuario ou rotina de salvamento.
- Latitude, longitude, fonte e data da geocodificacao devem ser gravadas no cadastro quando a localizacao for encontrada.
- Sempre que qualquer campo relevante do endereco for criado ou alterado, o sistema deve atualizar a geolocalizacao na propria tabela do cadastro.
- Campos que disparam atualizacao de geolocalizacao: CEP, Logradouro, Numero, Complemento quando influenciar localizacao, Bairro, Municipio, UF e Pais.
- Ao detectar alteracao de endereco, o sistema deve marcar GeoStatus como PENDENTE e limpar ou desconsiderar Latitude, Longitude, FonteGeo e DataGeo antigos.
- Apos salvar cadastro com endereco criado ou alterado, o sistema deve executar nova geocodificacao quando o endereco minimo estiver valido.
- Quando a geocodificacao retornar resultado valido, o sistema deve atualizar Latitude, Longitude, FonteGeo, DataGeo e GeoStatus = OK na tabela correspondente.
- Se a geocodificacao falhar, o cadastro pode ser salvo, mas deve ficar com GeoStatus = PENDENTE ou equivalente.
- Se o endereco estiver incompleto, o cadastro pode ser salvo, mas deve ficar com GeoStatus = INCOMPLETO ou equivalente.
- Se o endereco estiver vazio, o sistema nao deve gerar geolocalizacao.
- O sistema nao deve manter latitude/longitude antiga quando o endereco mudou.
- Orcamento nao pode ser gerado ou finalizado se o local do evento ou a sede necessaria ao calculo estiverem sem endereco, sem latitude/longitude, com GeoStatus PENDENTE ou com GeoStatus INCOMPLETO.
- O cache de CEP nao substitui a geolocalizacao; ele apenas auxilia o preenchimento textual do endereco.
- A geolocalizacao deve ser calculada com base no endereco completo, especialmente numero, logradouro, municipio, UF e pais.

## Sedes

- A empresa possui sedes operacionais em Porto Alegre e Santa Cruz do Sul.
- Deve existir uma sede fantasma para recursos em manutencao, conserto, lavagem, reposicao ou situacoes equivalentes.
- Sedes possuem endereco padronizado, CNPJ, responsavel, telefone/celular e demais dados de contato.
- Para calculo de orcamento, deve ser considerada a distancia entre o local do evento e as sedes operacionais.
- Se coordenadas ou geocodificacao forem indisponiveis ou duvidosas, a sede deve ser escolhida manualmente.
- A distancia e a sede escolhida no orcamento devem ser preservadas para manter o historico do calculo.

## Locais de Evento

- Local de evento deve conter nome, nome fantasia, endereco padronizado, CNPJ, telefone, celular, e-mail, site, tipo de local, contatos e quem indicou.
- Tipo de local deve ser ajustavel por arquivo JSON enquanto a lista definitiva estiver em estudo.
- Local pode possuir multiplos espacos/ambientes.
- Espacos registram nome, tipo interno/externo, capacidade, dimensoes e servicos oferecidos.

## Empresas, Convenios e Contratos

- Empresas cadastradas podem ser sindicatos, associacoes ou empresas em geral.
- Contratos com a MDM definem se a relacao e convenio, parceria ou patrocinio.
- Contrato define desconto quando aplicavel.
- Locais tambem podem possuir convenio.
- Quando houver desconto por local e por empresa, o desconto final deve ser o maior indicado por contrato.

## Clientes e Criancas

- Cliente solicita orcamento.
- Orcamento aprovado gera contrato.
- Deve haver cadastro do cliente e da crianca para a qual a festa sera realizada.
- Crianca deve possuir data de nascimento.
- Deve ser previsto registro de crianca especial conforme legislacao vigente, pois isso pode alterar regras de execucao do evento.

## Atores

- Ator registra dados pessoais e profissionais.
- O cadastro fisico do profissional inclui nome, nome profissional, endereco padronizado, nacionalidade, telefones, data de nascimento, CPF, RG, e-mail, ensino e sexo.

## Figurinos

- Figurino deve registrar nome longo, nome curto, data de aquisicao, sede/local onde esta e disponibilidade.
- Disponibilidade deve aceitar pelo menos: disponivel, higienizando e manutencao.
- Figurino deve registrar data do ultimo uso e ator que usou pela ultima vez.
- Data do ultimo uso e ator do ultimo uso sao atualizados a partir da conclusao do evento.

## Orcamento, Evento, Calendario e Financeiro

### Criacao do Orcamento

- Cliente solicita orcamento.
- O orcamento deve registrar cliente solicitante, crianca relacionada a festa, local da festa, data da festa, horario previsto, tempo de apresentacao e 1 ou mais personagens/figurinos desejados.
- O sistema deve permitir selecionar multiplos personagens/figurinos no mesmo orcamento.
- O sistema deve registrar o tempo de apresentacao solicitado.
- O orcamento pode iniciar em status RASCUNHO quando estiver incompleto.
- O orcamento deve ficar em status PENDENTE_COMPLEMENTACAO quando os dados principais foram informados e aguardam analise administrativa.
- O sistema deve validar se o local da festa possui endereco completo e geolocalizacao valida.
- O orcamento nao deve seguir para calculo final se o local nao possuir latitude/longitude valida.
- O orcamento esta ligado a local, cliente, crianca, figurino/personagem e ator quando definido.
- Orcamento possui data de criacao e data de execucao.

### Complementacao do Orcamento

- Administrador deve complementar o orcamento antes de enviar valor final ao cliente.
- Administrador deve pesquisar e selecionar ator adequado para cada personagem/figurino.
- O sistema deve permitir registrar ou calcular custo de deslocamento.
- O custo de deslocamento deve considerar a distancia entre a sede operacional e o local da festa.
- Para calculo de orcamento, deve ser considerada a distancia entre o local do evento e as sedes operacionais.
- A sede operacional pode ser sugerida automaticamente pela menor distancia.
- Se coordenadas ou geocodificacao forem indisponiveis ou duvidosas, a sede deve ser escolhida manualmente.
- A sede operacional usada no calculo deve ficar gravada no orcamento.
- A distancia usada no calculo deve ficar gravada no orcamento.
- A distancia e a sede escolhida no orcamento devem ser preservadas para manter o historico do calculo.
- Administrador deve revisar se o cliente possui convenio ativo.
- Administrador deve revisar se o local da festa possui convenio ativo.
- Quando houver desconto por local e por empresa/cliente, o desconto final deve ser o maior indicado por contrato.
- O sistema deve calcular o valor final considerando personagens/figurinos, tempo de apresentacao, atores selecionados, custo de deslocamento, desconto de convenio e ajustes manuais autorizados.
- O administrador deve informar o cliente sobre os valores envolvidos.
- Apos revisao, o orcamento deve mudar para status ENVIADO_AO_CLIENTE.

### Aprovacao do Orcamento

- Todo orcamento pode ser aprovado ou rejeitado.
- Administrador deve registrar o aceite do cliente.
- Ao registrar aceite, o orcamento deve mudar para status APROVADO.
- Orcamento aprovado deve gerar contrato quando aplicavel ao fluxo comercial.
- Orcamento aprovado deve gerar receita no modulo financeiro.
- O lancamento financeiro deve ficar em status AGUARDANDO_PAGAMENTO ate confirmacao de pagamento.
- O pagamento deve ser acompanhado ate o dia da festa.
- Orcamento aprovado deve gerar informacao no calendario interno do SMDM.
- Orcamento aprovado deve gerar registro no calendario para todos os administradores e atores envolvidos quando a integracao estiver ativa.
- Orcamento aprovado deve gerar roteiro operacional do evento.
- O calendario de atividades deve ser montado no Google Calendar em etapa de integracao.
- A empresa deve possuir uma conta Google propria para centralizar o calendario da MDM.
- O SMDM deve alimentar o Google Calendar a partir dos dados oficiais do sistema.
- Eventos de calendario devem ser enviados/compartilhados com atores e administradores envolvidos.
- A agenda interna do SMDM e a origem oficial; o Google Calendar funciona como sincronizacao para visualizacao, lembretes e compartilhamento pelo celular.
- O evento passa por quatro etapas: orcamento, aprovacao, execucao e conclusao.
- A conclusao do evento deve alimentar dados historicos relacionados ao uso de figurinos e atores.
- Data do ultimo uso e ator do ultimo uso do figurino devem ser atualizados a partir da conclusao do evento.

### Status do Orcamento

- RASCUNHO: orcamento iniciado, mas ainda incompleto.
- PENDENTE_COMPLEMENTACAO: cliente informou dados principais, mas falta analise administrativa.
- EM_ANALISE: administrador esta revisando atores, deslocamento, convenios e valores.
- ENVIADO_AO_CLIENTE: valor final foi informado ao cliente.
- APROVADO: cliente aceitou o orcamento.
- REJEITADO: cliente nao aceitou o orcamento.
- CANCELADO: orcamento foi cancelado internamente.
- CONVERTIDO_EVENTO: orcamento aprovado ja gerou contrato, calendario, roteiro e financeiro.

### Congelamento dos Dados do Orcamento

- Quando o orcamento for aprovado, o sistema deve preservar os dados usados no calculo.
- Devem ser gravados no proprio orcamento ou em tabelas filhas historicas: sede considerada, distancia considerada, custo de deslocamento, ator selecionado, personagem/figurino selecionado, tempo de apresentacao, desconto aplicado, origem do desconto, valor bruto, valor final, condicoes de pagamento, usuario que aprovou e data/hora da aprovacao.
- Alteracoes futuras em cliente, local, convenio, sede, ator ou figurino nao devem alterar o historico do orcamento aprovado.

