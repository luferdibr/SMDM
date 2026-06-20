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
- Em telas com muitos campos, a praticidade deve prevalecer sobre o desenho visual.
- Cadastros longos devem evitar uma unica tela extensa; devem ser divididos em abas, secoes recolhaveis ou passos curtos conforme o fluxo de trabalho.
- Campos de edicao principais e botoes de acao devem permanecer acessiveis durante a navegacao da lista ou do conteudo.
- A listagem de registros deve rolar de forma independente da area de edicao, evitando que a navegacao pela lista afaste os campos de alteracao.
- O sistema deve reduzir espacos verticais desnecessarios em telas de cadastro para diminuir rolagem e tempo de preenchimento.
- Telas de cadastro devem favorecer preenchimento rapido, revisao objetiva e salvamento frequente.
- Campos editaveis devem usar layout compacto, bem distribuido e organizado por secoes, abas ou grupos logicos.
- Campos mais usados devem ficar visiveis na primeira area da tela, evitando rolagem excessiva.
- As telas devem permitir operacao eficiente por teclado, incluindo Tab, Enter, atalhos e foco inicial correto.
- Listagens devem permitir busca, filtros, ordenacao e abertura rapida do registro.
- Campos de pesquisa de Local, Cliente, Ator, Empresa e Sede devem aceitar busca por CPF, CNPJ, nome ou telefone.
- A pesquisa padronizada de Local, Cliente, Ator, Empresa e Sede deve ser reutilizavel em orcamento, contratos e outras rotinas que precisem consultar essas informacoes.
- Rotinas operacionais nao devem criar criterios proprios de pesquisa quando puderem usar a rotina padrao.
- A rotina de pesquisa deve identificar automaticamente se o termo digitado representa CPF, CNPJ, telefone ou nome.
- CPF e CNPJ informados na pesquisa devem ser normalizados e validados pelos digitos verificadores.
- Telefone digitado em pesquisa deve ser tratado como sequencia de digitos, sem regra formal de validacao.
- Nome digitado em pesquisa deve ser tratado como texto.
- Como telefone celular pode ter 11 digitos, termo numerico puro de 11 digitos so deve ser classificado como CPF quando for CPF valido; caso contrario deve ser tratado como telefone. CPF formatado invalido deve ser tratado como CPF invalido.
- CNPJ com 14 digitos deve ser classificado como CNPJ e validado.
- Campos obrigatorios, opcionais, calculados e somente leitura devem ser claramente diferenciados.
- Mensagens de validacao devem ser diretas e proximas do campo com problema.
- Todo cadastro principal deve possuir identificador unico interno.
- Todo cadastro principal deve possuir status, preferencialmente ATIVO ou INATIVO.
- Registros usados em historico, orcamento, evento, contrato, financeiro, calendario ou movimentacao nao devem ser excluidos fisicamente.
- A regra padrao deve ser inativacao, nao exclusao fisica.
- Registros inativos nao devem aparecer como opcao padrao em novos lancamentos, mas devem aparecer em consultas historicas.
- Antes de excluir qualquer registro, o sistema deve avaliar as dependencias em outras tabelas.
- O sistema deve possuir regras de dependencia por cadastro/tabela para indicar quais tabelas podem estar vinculadas ao registro.
- As regras de dependencia devem informar a tabela origem, campo chave, tabela dependente, campo dependente, tipo de impacto e acao permitida.
- Quando existir dependencia ativa, historica, financeira, contratual, de calendario, orcamento, evento ou auditoria, a exclusao fisica deve ser bloqueada.
- Quando a exclusao for bloqueada por dependencia, o sistema deve informar ao usuario quais vinculos impedem a exclusao.
- A acao padrao para registro com dependencia deve ser inativar, preservando o historico e evitando novos usos.
- Exclusao fisica so deve ser permitida quando nao houver dependencia relevante e o registro nao fizer parte de historico operacional.
- Exclusao em cascata so deve ser permitida para dados auxiliares temporarios ou filhos sem valor historico proprio, quando explicitamente prevista na regra de dependencia.
- A rotina de instalacao deve criar ou atualizar a estrutura usada para armazenar as regras de dependencia quando essa estrutura for adotada.
- Todo cadastro deve registrar data de criacao, usuario criador, data da ultima alteracao e usuario da ultima alteracao.
- Campos obrigatorios devem ser validados antes de salvar.
- O sistema deve impedir duplicidade em campos criticos, como CPF, CNPJ, e-mail principal, nome de sede, nome de figurino ou codigo interno, conforme o tipo de cadastro.
- Em cadastros mestres, cada CPF ou CNPJ valido deve possuir apenas um cadastro ativo/principal por tabela de cadastro.
- A mesma pessoa/documento nao deve ser cadastrada duas vezes no mesmo cadastro mestre; a correcao deve ser feita editando o registro existente.
- Rotinas operacionais como orcamento podem repetir CPF/CNPJ em varios lancamentos, pois representam historico/transacoes e nao novo cadastro mestre.
- CPF e CNPJ digitados devem ser normalizados e validados pelos digitos verificadores antes de salvar.
- CPF deve conter 11 digitos numericos e CNPJ deve conter 14 digitos numericos apos remover mascara, pontos, barras, tracos e espacos.
- Em campos opcionais de CPF/CNPJ, valor vazio ou composto somente por zeros deve ser tratado como nao informado.
- Cadastros parciais devem ser permitidos quando o documento nao for obrigatorio, desde que os campos obrigatorios minimos do cadastro estejam validos.
- Regra geral de interface: todo campo de CPF ou CNPJ deve validar o documento ao sair do campo.
- Campos de CPF/CNPJ devem avisar documento invalido imediatamente ao sair do campo, sem depender apenas do botao Salvar.
- A validacao ao sair do campo nao substitui a validacao no salvamento; o servico tambem deve bloquear CPF/CNPJ invalido.
- O cadastro deve validar o documento pelo tipo informado ou pelo tamanho do documento, nao apenas pelo nome da tela.
- Cadastro de empresa pode usar CPF quando representar microempresa, MEI, produtor individual ou situacao equivalente em que o registro fiscal seja CPF.
- Quando empresa aceitar CNPJ/CPF, o campo deve bloquear documentos invalidos e permitir CPF valido sem exigir CNPJ.
- Alteracoes em dados sensiveis devem ser preparadas para auditoria em fase futura.

## Enderecos

- Cadastros com endereco devem seguir campos padronizados: CEP, Logradouro, Numero, Complemento, Bairro, Municipio, UF, Pais, Latitude, Longitude, FonteGeo e DataGeo quando aplicavel.
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
- Havendo GOOGLE_MAPS_API_KEY configurada, a geolocalizacao deve usar Google Maps Geocoding API.
- Na ausencia de GOOGLE_MAPS_API_KEY, a geolocalizacao deve usar Nominatim/geopy como alternativa gratuita.
- A geracao automatica de latitude/longitude deve ser controlada por configuracao do sistema.
- Quando AUTO_GEOCODING_ENABLED estiver desativado, o salvamento de cadastros com endereco nao deve chamar servico externo para geolocalizacao automaticamente.
- Quando a geracao automatica estiver desativada e nao houver coordenadas informadas manualmente, Latitude e Longitude devem ficar com zero, indicando geolocalizacao pendente ou nao gerada.
- Coordenadas preenchidas manualmente ou por rotina acionada pelo usuario podem ser preservadas mesmo com a geracao automatica desativada.
- Consultas ao Google Maps devem ser acompanhadas mensalmente porque podem gerar cobranca ao ultrapassar a franquia, credito ou limite contratado.
- O sistema deve registrar cada consulta feita ao Google Maps, incluindo servico, endereco/consulta, status, sucesso, detalhes e data/hora.
- Os limites mensais e alertas de uso do Google Maps devem ser configuraveis, nao fixos no codigo, pois podem mudar conforme regras comerciais do Google e APIs habilitadas.
- Ao atingir limite mensal ou limite de alerta configurado para Google Maps, o sistema deve registrar aviso para acompanhamento administrativo.
- Latitude, longitude, fonte e data da geocodificacao devem ser gravadas no cadastro quando a localizacao for encontrada.
- Sempre que qualquer campo relevante do endereco for criado ou alterado, o sistema deve atualizar a geolocalizacao na propria tabela do cadastro.
- Campos que disparam atualizacao de geolocalizacao: CEP, Logradouro, Numero, Complemento quando influenciar localizacao, Bairro, Municipio, UF e Pais.
- Apos salvar cadastro com endereco criado ou alterado, o sistema deve executar nova geocodificacao quando o endereco minimo estiver valido.
- Quando a geocodificacao retornar resultado valido, o sistema deve atualizar Latitude, Longitude, FonteGeo e DataGeo na tabela correspondente.
- Se a geocodificacao falhar, o cadastro pode ser salvo sem latitude/longitude.
- Se o endereco estiver incompleto, o cadastro pode ser salvo sem gerar geolocalizacao.
- Se o endereco estiver vazio, o sistema nao deve gerar geolocalizacao.
- O sistema nao deve manter latitude/longitude antiga quando o endereco mudou.
- Orcamento nao pode ser gerado ou finalizado se o local do evento ou a sede necessaria ao calculo estiverem sem endereco ou sem latitude/longitude.
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
- Local de evento pode registrar CPF em vez de CNPJ quando o local/prestador nao possuir CNPJ, como pessoa fisica, MEI ou situacao equivalente.
- O documento fiscal do local deve aceitar CPF com 11 digitos ou CNPJ com 14 digitos, validando pelo tipo/tamanho informado.
- Tipo de local deve ser ajustavel por arquivo JSON enquanto a lista definitiva estiver em estudo.
- Local pode possuir multiplos espacos/ambientes.
- Espacos registram nome, tipo interno/externo, capacidade, dimensoes e servicos oferecidos.
- Tipos de local devem permanecer como tabela de dominio editavel, disponivel no menu para manutencao administrativa.
- Ambientes e estruturas/infraestrutura devem ser administrados dentro da rotina de cadastro de local quando fizerem parte da composicao do local, sem obrigatoriedade de aparecerem como opcoes independentes no menu principal.
- A pesquisa web de locais nao deve gravar diretamente no cadastro oficial LocalEvento; dados captados devem passar pela tabela secundaria LocalEventoPesquisaWeb para pesquisa, analise, pontuacao, revisao e transferencia controlada.
- A pesquisa web automatica de locais deve usar todas as fontes gratuitas configuradas e sem chave disponiveis no sistema antes de depender de provedores pagos. Inicialmente, a coleta gratuita usa Nominatim/OpenStreetMap por termo e Overpass/OpenStreetMap para pontos de interesse no municipio.
- A pesquisa web automatica de locais deve priorizar municipios proximos as sedes operacionais Porto Alegre e Santa Cruz do Sul. Quando a tabela Municipio possuir campo REGIAO, a lista inicial deve agrupar primeiro os municipios da mesma REGIAO dessas sedes, deixando os demais municipios do RS em seguida.
- Na pesquisa web automatica de locais, somente resultados de cidade validada como municipio do Rio Grande do Sul na tabela Municipio, ou com CEP entre 90000-000 e 99999-999, podem seguir como candidatos ao cadastro automatico.
- Se o resultado pesquisado nao for de municipio validado do Rio Grande do Sul e nao possuir CEP na faixa 90000-000 a 99999-999, a pontuacao deve ser zerada e o registro deve ser marcado como NAO_SERVE.
- Se o resultado ja existir no cadastro oficial e for identificado que nao cumpre a regra de municipio do Rio Grande do Sul ou faixa de CEP do Rio Grande do Sul, a pontuacao tambem deve ser zerada e o registro de pesquisa deve ficar marcado como NAO_SERVE, mantendo referencia ao cadastro existente quando possivel.
- Local pesquisado na web so pode ser transferido ou sugerido para transferencia quando atingir pontuacao minima de 80 pontos e nao estiver descartado ou marcado como duplicidade critica.
- A tabela oficial LocalEvento deve manter campos de controle da origem web: CaptadoWeb, ComplementadoWeb, CadastroValidado, PesquisaIncompleta, NecessitaComplemento, NecessitaRevisao, PontuacaoOrigemWeb, FonteOrigemWeb, DataOrigemWeb, LocalPesquisaWebId, DataValidacaoCadastro e ObservacaoPesquisa.
- Local transferido da pesquisa web nasce como nao validado, necessitando revisao humana ate validacao por usuario autorizado.
- Dentro das opcoes de local devem existir rotinas separadas para pesquisa web, edicao do que foi pesquisado e transferencia controlada para o cadastro oficial.

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
- Cliente pode possuir um ou mais aniversariantes vinculados ao longo do tempo.
- Cada aniversariante vinculado ao cliente deve registrar nome, data de nascimento e grau de relacionamento com o cliente, como filho, sobrinho, enteado ou equivalente.
- Grau de relacionamento do aniversariante deve usar dominio controlado por configuracao, inicialmente em config/graus_relacionamento.json.
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
- O calculo de valores do orcamento deve usar como fontes de informacao: local, cliente, personagem/figurino, ator e distancia entre a sede operacional e o local do evento.
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
