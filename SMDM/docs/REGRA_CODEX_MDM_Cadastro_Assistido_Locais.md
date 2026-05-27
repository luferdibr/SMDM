# REGRA DE NEGÓCIO — MDM

## Cadastro Assistido de Locais por Pesquisa Web com Tabela Secundária

## 1\. Objetivo

Implementar no sistema MDM uma rotina de **captação assistida de locais** para pesquisar na web casas de festas, espaços para eventos, salões, buffets, sítios, chácaras e locais de aluguel para festas e eventos.

A pesquisa web **não deve gravar diretamente na tabela oficial de locais**.

Os dados encontrados devem ser gravados primeiro em uma **tabela secundária de pesquisa**, permitindo análise, pontuação, revisão, descarte, complementação e posterior transferência controlada para a tabela definitiva de locais.

Somente registros com **pontuação igual ou superior a 80 pontos** poderão ser transferidos automaticamente ou sugeridos para transferência para a tabela oficial de locais.

\---

## 2\. Conceito Geral

O cadastro oficial de locais deve permanecer confiável.

A pesquisa web deve funcionar como uma área intermediária de coleta, chamada neste documento de:

`\[MMPV].\[dbo].\[LocalEventoPesquisaWeb]`

Essa tabela conterá registros captados da internet, ainda não validados como cadastro oficial.

A tabela oficial continuará sendo:

`\[MMPV].\[dbo].\[LocalEvento]`

ou o nome equivalente já existente no sistema MDM.

\---

## 3\. Tipos de Locais a Pesquisar

A rotina deverá pesquisar termos como:

* Casa de festas
* Casa de festas infantil
* Espaço para eventos
* Salão de festas
* Salão de eventos
* Buffet infantil
* Buffet para festas
* Aluguel de espaço para festas
* Aluguel de espaço para eventos
* Centro de eventos
* Sítio para eventos
* Chácara para festas
* Local para festa infantil
* Local para casamento
* Local para aniversário
* Espaço kids para festas

Os termos devem ficar parametrizados para permitir manutenção sem alteração de código-fonte.

\---

## 4\. Dados a Coletar na Pesquisa Web

A rotina deve tentar coletar o máximo possível dos seguintes dados:

* Nome do local
* Tipo sugerido do local
* Descrição pública
* Endereço
* Número
* Complemento
* Bairro
* Cidade
* UF
* CEP
* Latitude
* Longitude
* Telefone
* WhatsApp
* E-mail
* Site
* Instagram
* Facebook
* Outras redes sociais
* Horário de funcionamento
* Fonte da informação
* URL da fonte
* Data e hora da pesquisa
* Grau de confiabilidade
* Status da pesquisa

\---

## 5\. Tabela Secundária de Pesquisa

Criar uma tabela secundária para armazenar os dados captados pela web.

Nome sugerido:

`TB\\\\\\\_LocalPesquisaWeb`

### Estrutura sugerida

```sql
CREATE TABLE \[MMPV].\[dbo].\[LocalEventoPesquisaWeb] (

         \[LocalEventoID] \[int] IDENTITY(1,1) NOT NULL,

         \[TipoLocalSugerido] VARCHAR(100) NULL,

         \[NomeCasa] \[varchar](100) NOT NULL,

         \[Endereco] \[varchar](255) NULL,

         \[Responsavel] \[varchar](100) NULL,

         \[Contato] \[varchar](50) NULL,

         \[PossuiEstacionamento] \[bit] NULL,

         \[Observacoes] \[text] NULL,

         \[SharePointID] \[int] NULL,

         \[LocTipoID] \[int] NULL,

         \[CEP] \[nvarchar](20) NULL,

         \[Logradouro] \[nvarchar](200) NULL,

         \[Numero] \[nvarchar](30) NULL,

         \[Complemento] \[nvarchar](100) NULL,

         \[Bairro] \[nvarchar](100) NULL,

         \[Municipio] \[nvarchar](100) NULL,

         \[UF] \[nvarchar](2) NULL,

         \[Pais] \[nvarchar](80) NOT NULL,

         \[Telefone] \[nvarchar](30) NULL,

         \[Celular] \[nvarchar](30) NULL,

         \[Email] \[nvarchar](200) NULL,

         \[Numero] \[nvarchar](30) NULL,

         \[Complemento] \[nvarchar](100) NULL,

         \[Bairro] \[nvarchar](100) NULL,

         \[Municipio] \[nvarchar](100) NULL,

         \[UF] \[nvarchar](2) NULL,

         \[Pais] \[nvarchar](80) NOT NULL,

         \[Telefone] \[nvarchar](30) NULL,

         \[Celular] \[nvarchar](30) NULL,

         \[Email] \[nvarchar](200) NULL,

         \[Site]  \[VARCHAR](250) NULL,
         \[Instagram]  \[VARCHAR(250) NULL,
         \[Facebook]  \[VARCHAR(250) NULL,
         \[OutrasRedes]  \[TEXT] NULL,

         \[Latitude] \[decimal](10, 7) NULL,

         \[Longitude] \[decimal](10, 7) NULL,

         \[FonteGeo] \[nvarchar](50) NULL,

         \[DataGeo] \[datetime] NULL,

         \[Ativo] \[bit] NOT NULL,

         \[CriadoEm] \[datetime] NOT NULL,

         \[AtualizadoEm] \[datetime] NULL,

         \[NomeFantasia] \[nvarchar](200) NULL,
         \[CNPJ] \[nvarchar](20) NULL,

         \[Site] \[nvarchar](250) NULL,

         \[Contato1Nome] \[nvarchar](200) NULL,

         \[Contato1Telefone] \[nvarchar](30) NULL,

         \[Contato1Cargo] \[nvarchar](120) NULL,

         \[Contato2Nome] \[nvarchar](200) NULL,

         \[Contato2Telefone] \[nvarchar](30) NULL,

         \[Contato2Cargo] \[nvarchar](120) NULL,

         \[Contato3Nome] \[nvarchar](200) NULL,

         \[Contato3Telefone] \[nvarchar](30) NULL,

         \[Contato3Cargo] \[nvarchar](120) NULL,

         \[QuemIndicou] \[nvarchar](200)  DEFAULT 'Pesquisa Web Automática',

         \[HorarioFuncionamento] \[TEXT] NULL,

         \[FontePrincipal] \[VARCHAR] (100) NULL,
	 \[UrlFonte] \[VARCHAR] (500) NULL,
	 \[DadosBrutos] \[TEXT] NULL,

	 \[PontuacaoConfiabilidade] \[DECIMAL] (5,2) DEFAULT 0,
	 \[StatusPesquisa] \[VARCHAR] (30) DEFAULT 'PENDENTE\\\\\\\_ANALISE',

	\[PossivelDuplicidade] \[BIT] DEFAULT 0,
	\[LocalExistenteId] \[INT] NULL,

	\[Transferido] \[BIT] DEFAULT 0,
	\[DataTransferencia] \[DATETIME] NULL,
	\[UsuarioTransferenciaId] \[INT] NULL,

	\[Descartado] \[BIT] DEFAULT 0,
	\[DataDescarte] \[DATETIME] NULL,
	\[UsuarioDescarteId] \[INT] NULL,
	\[MotivoDescarte] \[TEXT] NULL,

	\[NecessitaComplemento] \[BIT] DEFAULT 1,
	\[NecessitaRevisao] \[BIT] DEFAULT 1,

	\[DataPesquisa] \[DATETIME] DEFAULT GETDATE(),
	\[DataUltimaAtualizacao] \[DATETIME] NULL,
	\[ObservacaoPesquisa] \[TEXT NULL
);
```

\---

## 6\. Status da Pesquisa

O campo `StatusPesquisa` deve aceitar os seguintes valores:

```text
PENDENTE\\\\\\\_ANALISE
PONTUACAO\\\\\\\_BAIXA
APTO\\\\\\\_TRANSFERENCIA
POSSIVEL\\\\\\\_DUPLICIDADE
TRANSFERIDO
DESCARTADO
DADOS\\\\\\\_CONFLITANTES
ERRO\\\\\\\_COLETA
```

### Regras de status

* `PENDENTE\\\\\\\_ANALISE`: registro recém-coletado.
* `PONTUACAO\\\\\\\_BAIXA`: pontuação menor que 80.
* `APTO\\\\\\\_TRANSFERENCIA`: pontuação igual ou superior a 80 e sem duplicidade crítica.
* `POSSIVEL\\\\\\\_DUPLICIDADE`: há possibilidade de o local já existir na tabela oficial.
* `TRANSFERIDO`: registro já transferido para a tabela oficial.
* `DESCARTADO`: registro descartado por usuário autorizado.
* `DADOS\\\\\\\_CONFLITANTES`: informações incompatíveis entre fontes.
* `ERRO\\\\\\\_COLETA`: houve erro durante a coleta.

\---

## 7\. Regra de Pontuação

A pontuação deve variar de 0 a 100 pontos.

Pontuação sugerida:

```text
Nome do local encontrado:                 +15
Cidade e UF encontrados:                  +10
Endereço encontrado:                      +15
Bairro encontrado:                         +5
CEP encontrado:                            +5
Latitude e longitude encontradas:         +15
Telefone ou WhatsApp encontrado:          +10
Site ou rede social encontrada:           +10
Tipo do local identificado:               +10
Fonte considerada confiável:               +5
```

Total máximo: 100 pontos.

\---

## 8\. Regra para Transferência

Um registro da tabela `TB\\\\\\\_LocalPesquisaWeb` somente poderá ser transferido para a tabela oficial `TB\\\\\\\_Local` quando atender às seguintes condições mínimas:

```text
PontuacaoConfiabilidade >= 80
Transferido = 0
Descartado = 0
StatusPesquisa = 'APTO\\\\\\\_TRANSFERENCIA'
```

Além disso, deve possuir obrigatoriamente:

```text
NomeLocal
Cidade
UF
TipoLocalSugerido
Endereço ou Latitude/Longitude
```

Se não possuir esses dados mínimos, mesmo com pontuação alta, o registro deve permanecer como `PENDENTE\\\\\\\_ANALISE` ou `DADOS\\\\\\\_CONFLITANTES`.

\---

## 9\. Regra de Duplicidade

Antes da transferência, o sistema deve verificar se o local já existe na tabela oficial.

Critérios de comparação:

* Nome semelhante
* Mesma cidade
* Mesmo bairro
* Endereço semelhante
* Telefone igual
* Latitude/longitude próximas
* Site ou rede social igual

Se houver possível duplicidade:

```text
PossivelDuplicidade = 1
StatusPesquisa = 'POSSIVEL\\\\\\\_DUPLICIDADE'
LocalExistenteId = Id do possível local existente
```

Nesse caso, o sistema não deve criar novo cadastro automaticamente.

Deve oferecer ao usuário as opções:

```text
1. Complementar cadastro existente
2. Criar novo local mesmo assim
3. Descartar registro pesquisado
4. Manter pendente para análise posterior
```

\---

## 10\. Rotina de Transferência para a Tabela Oficial

Criar uma rotina chamada, por exemplo:

`transferir\\\\\\\_local\\\\\\\_pesquisa\\\\\\\_para\\\\\\\_cadastro()`

Essa rotina deve:

1. Receber o `Id` da tabela `TB\\\\\\\_LocalPesquisaWeb`.
2. Validar se a pontuação é maior ou igual a 80.
3. Verificar se o registro já foi transferido.
4. Verificar se o registro foi descartado.
5. Verificar duplicidade na tabela oficial.
6. Criar registro na tabela oficial `TB\\\\\\\_Local` ou complementar um registro existente, conforme decisão do usuário.
7. Marcar o registro da pesquisa como transferido.
8. Registrar data, usuário e log de auditoria.

\---

## 11\. Complementação de Cadastro Existente

Quando o registro pesquisado corresponder a um local já existente, o sistema poderá complementar dados vazios da tabela oficial.

Regra:

* Campos vazios podem ser preenchidos automaticamente.
* Campos já preenchidos e não validados podem ser sugeridos para substituição.
* Campos já validados manualmente não devem ser substituídos sem confirmação explícita.

\---

## 12\. Campos de Controle na Tabela Oficial de Locais

Adicionar ou manter na tabela oficial de locais os seguintes campos de controle:

```sql
CaptadoWeb BIT DEFAULT 0,
ComplementadoWeb BIT DEFAULT 0,
CadastroValidado BIT DEFAULT 0,
PesquisaIncompleta BIT DEFAULT 0,
NecessitaComplemento BIT DEFAULT 0,
NecessitaRevisao BIT DEFAULT 0,
PontuacaoOrigemWeb DECIMAL(5,2) NULL,
FonteOrigemWeb VARCHAR(100) NULL,
DataOrigemWeb DATETIME NULL,
LocalPesquisaWebId INT NULL,
DataValidacaoCadastro DATETIME NULL,
ObservacaoPesquisa TEXT NULL
```

### Significado

* `CaptadoWeb`: indica que o local nasceu da pesquisa web.
* `ComplementadoWeb`: indica que o local recebeu dados vindos da web.
* `CadastroValidado`: indica que o cadastro foi validado por usuário autorizado.
* `PesquisaIncompleta`: indica que a origem web trouxe dados parciais.
* `NecessitaComplemento`: indica ausência de dados importantes.
* `NecessitaRevisao`: indica que o cadastro ainda precisa de revisão humana.
* `PontuacaoOrigemWeb`: registra a pontuação recebida na origem.
* `FonteOrigemWeb`: registra a principal fonte da informação.
* `DataOrigemWeb`: registra quando a informação foi captada.
* `LocalPesquisaWebId`: vincula o local oficial ao registro de pesquisa que originou ou complementou o cadastro.

\---

## 13\. Regra de Gravação na Tabela Oficial

Ao transferir um registro da pesquisa para a tabela oficial:

```text
CaptadoWeb = 1
CadastroValidado = 0
NecessitaRevisao = 1
PontuacaoOrigemWeb = PontuacaoConfiabilidade da tabela de pesquisa
FonteOrigemWeb = FontePrincipal da tabela de pesquisa
DataOrigemWeb = DataPesquisa da tabela de pesquisa
LocalPesquisaWebId = Id da tabela de pesquisa
```

Se algum dado importante continuar faltando:

```text
PesquisaIncompleta = 1
NecessitaComplemento = 1
```

Mesmo com pontuação acima de 80, o cadastro transferido ainda deve ser considerado não validado até conferência humana.

\---

## 14\. Validação Manual

Somente usuário autorizado poderá validar definitivamente o cadastro.

Ao validar:

```text
CadastroValidado = 1
NecessitaRevisao = 0
DataValidacaoCadastro = data/hora atual
```

A validação não obriga que `NecessitaComplemento` seja zerado. Um cadastro pode estar validado e ainda precisar de dados complementares não obrigatórios.

\---

## 15\. Auditoria

Toda ação deve gerar log de auditoria:

```text
CAPTACAO\\\\\\\_WEB
ANALISE\\\\\\\_PESQUISA\\\\\\\_WEB
TRANSFERENCIA\\\\\\\_LOCAL\\\\\\\_WEB
COMPLEMENTACAO\\\\\\\_LOCAL\\\\\\\_WEB
DESCARTE\\\\\\\_LOCAL\\\\\\\_WEB
VALIDACAO\\\\\\\_CADASTRO\\\\\\\_LOCAL
ALTERACAO\\\\\\\_MANUAL\\\\\\\_LOCAL
```

O log deve conter:

* Usuário
* Data/hora
* Registro da tabela de pesquisa
* Registro da tabela oficial, quando existir
* Campos alterados
* Pontuação
* Fonte da informação
* Tipo da ação

\---

## 16\. Tela de Análise da Pesquisa Web

Criar tela administrativa para análise dos locais captados.

Filtros mínimos:

```text
StatusPesquisa
Cidade
UF
TipoLocalSugerido
Pontuação mínima
Possível duplicidade
Transferido
Descartado
Necessita complemento
```

A tela deve permitir:

```text
Visualizar dados coletados
Comparar com local existente
Transferir para cadastro oficial
Complementar local existente
Descartar registro
Recalcular pontuação
Editar dados antes da transferência
```

\---

## 17\. Regra de Uso em Orçamento

Apenas locais transferidos para a tabela oficial podem ser usados diretamente em orçamento.

Registros existentes apenas em `TB\\\\\\\_LocalPesquisaWeb` não devem aparecer como locais definitivos.

Porém, a tela de orçamento poderá oferecer uma opção:

```text
Pesquisar novo local na web
```

Ao escolher um local pesquisado com pontuação maior ou igual a 80, o sistema deve transferir ou solicitar confirmação de transferência antes de usar no orçamento.

\---

## 18\. Resultado Esperado

O MDM deverá possuir uma camada intermediária segura para captação de locais pela web.

A pesquisa web alimenta uma tabela secundária.

A tabela oficial de locais recebe apenas registros aprovados pela regra de pontuação e controle de duplicidade.

A pontuação mínima para transferência será de 80 pontos.

Mesmo após transferência, o cadastro deverá permanecer marcado como necessitando revisão humana até validação por usuário autorizado.

Essa regra evita poluir o cadastro oficial com dados incompletos, duplicados ou de baixa confiabilidade, mantendo o cadastro de locais útil para orçamento, cálculo de deslocamento, geolocalização e planejamento de eventos.

