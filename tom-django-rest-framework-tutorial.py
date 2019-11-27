# tom-django-rest-framework-tutorial.py
# tomazmcn@gmail.com
# https://github.com/tomazcunha/Tom-Django-Rest-Framework-Tutorial
# https://www.django-rest-framework.org/tutorial/quickstart/


# ##############################################################################
# ##############################################################################
# ##############################################################################
# ##############################################################################
19-11-2019 23:39

	

	# ------------------------------------------------------------------------------

	# Tutorial 1: Serialização

	# Introdução

		# Este tutorial abordará a criação de um código pastebin simples, destacando a API da Web. Ao longo do caminho, ele apresentará os vários componentes que compõem a estrutura REST e fornecerá uma compreensão abrangente de como tudo se encaixa.

		# O tutorial é bastante detalhado, portanto, você provavelmente deve obter um biscoito e uma xícara de sua bebida favorita antes de começar. Se você deseja apenas uma visão geral rápida, consulte a documentação de início rápido.

		# Nota : O código deste tutorial está disponível no repositório encode / rest-framework-tutorial no GitHub. A implementação concluída também está online como uma versão sandbox para teste, disponível aqui.


	# Configurando um Novo Ambiente

		# Antes de fazer qualquer outra coisa, criaremos um novo ambiente virtual, usando venv. Isso garantirá que nossa configuração de pacote seja mantida bem isolada de qualquer outro projeto em que estamos trabalhando. 

			# tom
			sudo apt-get install python3-venv


			python3 -m venv env

			source env/bin/activate


		# Agora que estamos dentro de um ambiente virtual, podemos instalar nossos requisitos de pacote.

			pip install django
			pip install djangorestframework
			pip install pygments  # We'll be using this for the code highlighting


			# tom
			pip freeze > requirements.txt

			cat requirements.txt
				# cat requirements.txt 
				# Django==2.2.7
				# djangorestframework==3.10.3
				# pkg-resources==0.0.0
				# Pygments==2.4.2
				# pytz==2019.3
				# sqlparse==0.3.0


		# Nota: Para sair do ambiente virtual a qualquer momento, basta digitar deactivate . Para mais informações, consulte a documentação venv.


	# ------------------------------------------------------------------------------
	# Começando

		# Ok, estamos prontos para a codificação. Para começar, vamos criar um novo projeto para trabalhar.

			cd ~
			django-admin startproject tutorial
			cd tutorial


		# Feito isso, podemos criar um aplicativo que usaremos para criar uma API da Web simples.

			python manage.py startapp snippets


		# Precisamos adicionar nosso novo aplicativo de snippets e o aplicativo rest_framework ao INSTALLED_APPS. Vamos editar o arquivo tutorial/settings.py:

			INSTALLED_APPS = [
			    ...
			    'rest_framework',
			    'snippets.apps.SnippetsConfig',
			]


		# Ok, estamos prontos para rolar.


	# ------------------------------------------------------------------------------
	# Criando um modelo para trabalhar

		# Para os propósitos deste tutorial, começaremos criando um modelo de Snippet simples que é usado para armazenar trechos de código. Vá em frente e edite o arquivo snippets/models.py . Nota: Boas práticas de programação incluem comentários. Embora você os encontre em nossa versão do repositório deste código de tutorial, os omitimos aqui para focar no próprio código.

			from django.db import models
			from pygments.lexers import get_all_lexers
			from pygments.styles import get_all_styles

			LEXERS = [item for item in get_all_lexers() if item[1]]
			LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
			STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])


			class Snippet(models.Model):
			    created = models.DateTimeField(auto_now_add=True)
			    title = models.CharField(max_length=100, blank=True, default='')
			    code = models.TextField()
			    linenos = models.BooleanField(default=False)
			    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
			    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)

			    class Meta:
			        ordering = ['created']



		# Também precisamos criar uma migração inicial para o nosso modelo de snippet e sincronizar o banco de dados pela primeira vez.

			python manage.py makemigrations snippets
			python manage.py migrate



	# ------------------------------------------------------------------------------
	# Criando uma classe Serializer

		# A primeira coisa que precisamos para começar em nossa API da Web é fornecer uma maneira de serializar e desserializar as instâncias de snippet em representações como json. Podemos fazer isso declarando serializadores que funcionam de maneira muito semelhante às Django's forms. Crie um arquivo no diretório de snippets denominado serializers.py e adicione o seguinte.

			from rest_framework import serializers
			from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES


			class SnippetSerializer(serializers.Serializer):
			    id = serializers.IntegerField(read_only=True)
			    title = serializers.CharField(required=False, allow_blank=True, max_length=100)
			    code = serializers.CharField(style={'base_template': 'textarea.html'})
			    linenos = serializers.BooleanField(required=False)
			    language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
			    style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')

			    def create(self, validated_data):
			        """
			        Create and return a new `Snippet` instance, given the validated data.
			        """
			        return Snippet.objects.create(**validated_data)

			    def update(self, instance, validated_data):
			        """
			        Update and return an existing `Snippet` instance, given the validated data.
			        """
			        instance.title = validated_data.get('title', instance.title)
			        instance.code = validated_data.get('code', instance.code)
			        instance.linenos = validated_data.get('linenos', instance.linenos)
			        instance.language = validated_data.get('language', instance.language)
			        instance.style = validated_data.get('style', instance.style)
			        instance.save()
			        return instance



		# A primeira parte da classe serializador define os campos que são serializados / desserializados. Os métodos create() e update() definem como instâncias de pleno direito são criadas ou modificadas ao chamar serializer.save()

		# Uma classe serializador é muito semelhante a uma classe Django Form e inclui sinalizadores de validação semelhantes nos vários campos, como required, max_length e default.

		# Os sinalizadores de campo também podem controlar como o serializador deve ser exibido em determinadas circunstâncias, como na renderização em HTML. O {'base_template': 'textarea.html'} acima é equivalente a usar widget=widgets.Textarea em uma classe Django Form. Isso é particularmente útil para controlar como a API navegável deve ser exibida, como veremos mais adiante no tutorial.

		# Na verdade, também podemos economizar algum tempo usando a classe ModelSerializer, como veremos mais adiante, mas por enquanto manteremos nossa definição de serializador explícita.
		


	# ------------------------------------------------------------------------------
	# Trabalhando com serializadores

		# Antes de prosseguir, vamos nos familiarizar com o uso de nossa nova classe Serializer. Vamos entrar no shell do Django.

			python manage.py shell 


		# Ok, assim que tivermos algumas importações fora do caminho, vamos criar alguns trechos de código para trabalhar.

			from snippets.models import Snippet
			from snippets.serializers import SnippetSerializer
			from rest_framework.renderers import JSONRenderer
			from rest_framework.parsers import JSONParser

			snippet = Snippet(code='foo = "bar"\n')
			snippet.save()

			snippet = Snippet(code='print("hello, world")\n')
			snippet.save()



		# Agora temos algumas instâncias de trechos para brincar. Vamos dar uma olhada em serializar uma dessas instâncias.

			serializer = SnippetSerializer(snippet)
			serializer.data
			# {'id': 2, 'title': '', 'code': 'print("hello, world")\n', 'linenos': False, 'language': 'python', 'style': 'friendly'}



		# Neste ponto, traduzimos a instância do modelo em tipos de dados nativos do Python. Para finalizar o processo de serialização, renderizamos os dados em json .

			content = JSONRenderer().render(serializer.data)
			content
			# b'{"id": 2, "title": "", "code": "print(\\"hello, world\\")\\n", "linenos": false, "language": "python", "style": "friendly"}'


		# A desserialização é semelhante. Primeiro, analisamos um fluxo em tipos de dados nativos do Python ...

			import io

			stream = io.BytesIO(content)
			data = JSONParser().parse(stream)


		# ... então restauramos esses tipos de dados nativos em uma instância de objeto totalmente preenchida.

			serializer = SnippetSerializer(data=data)
			serializer.is_valid()
			# True
			serializer.validated_data
			# OrderedDict([('title', ''), ('code', 'print("hello, world")\n'), ('linenos', False), ('language', 'python'), ('style', 'friendly')])
			serializer.save()
			# <Snippet: Snippet object>


		# Observe como a API é semelhante ao trabalho com formulários. A semelhança deve se tornar ainda mais aparente quando começamos a escrever vistas que usam nosso serializador.

		# Também podemos serializar conjuntos de consultas em vez de instâncias de modelo. Para isso, basta adicionar um sinalizador many=True aos argumentos do serializador.

			serializer = SnippetSerializer(Snippet.objects.all(), many=True)
			serializer.data
			# [OrderedDict([('id', 1), ('title', ''), ('code', 'foo = "bar"\n'), ('linenos', False), ('language', 'python'), ('style', 'friendly')]), OrderedDict([('id', 2), ('title', ''), ('code', 'print("hello, world")\n'), ('linenos', False), ('language', 'python'), ('style', 'friendly')]), OrderedDict([('id', 3), ('title', ''), ('code', 'print("hello, world")'), ('linenos', False), ('language', 'python'), ('style', 'friendly')])]



	# ------------------------------------------------------------------------------
	# Usando ModelSerializers

		# Nossa classe SnippetSerializer está replicando muitas informações que também estão contidas no modelo de Snippet. Seria bom se pudéssemos manter nosso código um pouco mais conciso.

		# Da mesma maneira que o Django fornece as classes Form e ModelForm, a estrutura REST inclui as classes Serializer e ModelSerializer .

		# Vejamos a refatoração do nosso serializador usando a classe ModelSerializer. Abra o arquivo snippets/serializers.py novamente e substitua a classe SnippetSerializer pela seguinte.

			class SnippetSerializer(serializers.ModelSerializer):
			    class Meta:
			        model = Snippet
			        fields = ['id', 'title', 'code', 'linenos', 'language', 'style']


		# Uma boa propriedade que os serializadores possuem é que você pode inspecionar todos os campos em uma instância do serializador, imprimindo sua representação. Abra o shell do Django com o python manage.py shell e tente o seguinte:

			from snippets.serializers import SnippetSerializer
			serializer = SnippetSerializer()
			print(repr(serializer))
			# SnippetSerializer():
			#    id = IntegerField(label='ID', read_only=True)
			#    title = CharField(allow_blank=True, max_length=100, required=False)
			#    code = CharField(style={'base_template': 'textarea.html'})
			#    linenos = BooleanField(required=False)
			#    language = ChoiceField(choices=[('Clipper', 'FoxPro'), ('Cucumber', 'Gherkin'), ('RobotFramework', 'RobotFramework'), ('abap', 'ABAP'), ('ada', 'Ada')...
			#    style = ChoiceField(choices=[('autumn', 'autumn'), ('borland', 'borland'), ('bw', 'bw'), ('colorful', 'colorful')...



		# É importante lembrar que as classes ModelSerializer não fazem nada particularmente mágico, elas são simplesmente um atalho para criar classes serializadoras:

		    # Um conjunto de campos determinado automaticamente.
		    # Implementações padrão simples para os métodos create() e update(). 



	# ------------------------------------------------------------------------------
	# Gravando visualizações regulares do Django usando nosso Serializer

	# Vamos ver como podemos escrever algumas visualizações de API usando nossa nova classe Serializer. Por enquanto não usaremos nenhum dos outros recursos da estrutura REST, apenas escreveremos as visualizações como visualizações regulares do Django.

	# Edite o arquivo snippets/views.py e adicione o seguinte.

		from django.http import HttpResponse, JsonResponse
		from django.views.decorators.csrf import csrf_exempt
		from rest_framework.parsers import JSONParser
		from snippets.models import Snippet
		from snippets.serializers import SnippetSerializer


	# A raiz da nossa API será uma visualização que suporta a listagem de todos os trechos existentes ou a criação de um novo trecho.

		@csrf_exempt
		def snippet_list(request):
		    """
		    List all code snippets, or create a new snippet.
		    """
		    if request.method == 'GET':
		        snippets = Snippet.objects.all()
		        serializer = SnippetSerializer(snippets, many=True)
		        return JsonResponse(serializer.data, safe=False)

		    elif request.method == 'POST':
		        data = JSONParser().parse(request)
		        serializer = SnippetSerializer(data=data)
		        if serializer.is_valid():
		            serializer.save()
		            return JsonResponse(serializer.data, status=201)
		        return JsonResponse(serializer.errors, status=400)



	# Observe que, como queremos poder POSTAR para essa visualização de clientes que não terão um token CSRF, precisamos marcar a visualização como csrf_exempt. Isso não é algo que você normalmente gostaria de fazer, e as exibições da estrutura REST na verdade usam um comportamento mais sensível do que isso, mas servirá para nossos propósitos agora.

	# Também precisaremos de uma visualização que corresponda a um snippet individual e possa ser usada para recuperar, atualizar ou excluir o snippet.

		@csrf_exempt
		def snippet_detail(request, pk):
		    """
		    Retrieve, update or delete a code snippet.
		    """
		    try:
		        snippet = Snippet.objects.get(pk=pk)
		    except Snippet.DoesNotExist:
		        return HttpResponse(status=404)

		    if request.method == 'GET':
		        serializer = SnippetSerializer(snippet)
		        return JsonResponse(serializer.data)

		    elif request.method == 'PUT':
		        data = JSONParser().parse(request)
		        serializer = SnippetSerializer(snippet, data=data)
		        if serializer.is_valid():
		            serializer.save()
		            return JsonResponse(serializer.data)
		        return JsonResponse(serializer.errors, status=400)

		    elif request.method == 'DELETE':
		        snippet.delete()
		        return HttpResponse(status=204)



	# Finalmente, precisamos conectar essas views. Crie o arquivo snippets/urls.py :

		from django.urls import path
		from snippets import views

		urlpatterns = [
		    path('snippets/', views.snippet_list),
		    path('snippets/<int:pk>/', views.snippet_detail),
		]


	# Também precisamos conectar o urlconf raiz, no arquivo tutorial/urls.py, para incluir os URLs do aplicativo de snippet.

		from django.urls import path, include

		urlpatterns = [
		    path('', include('snippets.urls')),
		]


	# Vale a pena notar que existem alguns casos extremos com os quais não estamos lidando adequadamente no momento. Se enviarmos json malformado ou se uma solicitação for feita com um método que a exibição não lida, terminaremos com uma resposta de 500 "erro do servidor". Ainda assim, isso serve por enquanto.



	# ------------------------------------------------------------------------------
	# Testando nossa primeira tentativa de uma API da Web

	# Agora podemos iniciar um servidor de amostra que serve nossos snippets.

	# Saia do shell ...

		quit() 

	# ... e inicie o servidor de desenvolvimento do Django.

		python manage.py runserver

		Validating models...

		0 errors found
		Django version 1.11, using settings 'tutorial.settings'
		Development server is running at http://127.0.0.1:8000/
		Quit the server with CONTROL-C.


	# Em outra janela do terminal, podemos testar o servidor.

	# Podemos testar nossa API usando curl ou httpie. Httpie é um cliente http amigável, escrito em Python. Vamos instalar isso.

	# Você pode instalar o httpie usando o pip:

		pip install httpie 


	# Por fim, podemos obter uma lista de todos os trechos:

		http http://127.0.0.1:8000/snippets/

		HTTP/1.1 200 OK
		...
		[
		  {
		    "id": 1,
		    "title": "",
		    "code": "foo = \"bar\"\n",
		    "linenos": false,
		    "language": "python",
		    "style": "friendly"
		  },
		  {
		    "id": 2,
		    "title": "",
		    "code": "print(\"hello, world\")\n",
		    "linenos": false,
		    "language": "python",
		    "style": "friendly"
		  }
		]



	# Ou podemos obter um snippet específico referenciando seu ID:

		http http://127.0.0.1:8000/snippets/2/

		HTTP/1.1 200 OK
		...
		{
		  "id": 2,
		  "title": "",
		  "code": "print(\"hello, world\")\n",
		  "linenos": false,
		  "language": "python",
		  "style": "friendly"
		}


	# Da mesma forma, você pode exibir o mesmo json visitando esses URLs em um navegador da web.


	# ------------------------------------------------------------------------------
	# Onde estamos agora

	# Até agora, estamos bem, temos uma API de serialização que se parece muito com a API de formulários do Django e algumas visualizações regulares do Django.

	# Nossas visualizações de API não fazem nada de especial no momento, além de json respostas json, e há alguns casos de erros de manipulação de borda que ainda gostaríamos de limpar, mas é uma API da Web em funcionamento.

	# Vamos ver como podemos começar a melhorar as coisas na parte 2 do tutorial . 



20-11-2019 02:30



# ##############################################################################
# ##############################################################################
# ##############################################################################
# ##############################################################################
20-11-2019 17:20

	# 2 - Requests and responses - Django REST framework
	https://www.django-rest-framework.org/tutorial/2-requests-and-responses/


	# Tutorial 2: Solicitações e Respostas

	# A partir deste ponto, começaremos realmente a cobrir o núcleo da estrutura REST. Vamos apresentar alguns blocos de construção essenciais.


	# Solicitar objetos

		# A estrutura REST apresenta um objeto Request que estende o HttpRequest regular e fornece uma análise de solicitação mais flexível. A funcionalidade principal do objeto Request é o atributo request.data, semelhante ao request.POST, mas mais útil para trabalhar com APIs da Web.

			request.POST  # Only handles form data.  Only works for 'POST' method.
			request.data  # Handles arbitrary data.  Works for 'POST', 'PUT' and 'PATCH' methods.


	# Objetos de resposta

		# A estrutura REST também apresenta um objeto Response, que é um tipo de TemplateResponse que pega conteúdo não renderizado e usa a negociação de conteúdo para determinar o tipo de conteúdo correto para retornar ao cliente.

			return Response(data)  # Renders to content type as requested by the client.


	# Códigos de status

		# O uso de códigos de status HTTP numéricos em suas visualizações nem sempre é uma leitura óbvia, e é fácil não notar se você errar um código de erro. A estrutura REST fornece identificadores mais explícitos para cada código de status, como HTTP_400_BAD_REQUEST no módulo de status . É uma boa idéia usá-los em vez de usar identificadores numéricos.
		

	# Agrupando visualizações da API

		# A estrutura REST fornece dois wrappers que você pode usar para gravar visualizações de API.

		    # O decorador @api_view para trabalhar com visualizações baseadas em funções.
		    # A classe APIView para trabalhar com visualizações baseadas em classe. 

		# Esses wrappers fornecem alguns bits de funcionalidade, como garantir que você receba instâncias de Request em sua visualização e adicionar contexto aos objetos de Response para que a negociação de conteúdo possa ser executada.

		# Os wrappers também fornecem comportamentos como retorno de respostas 405 Method Not Allowed quando apropriado e manipulação de qualquer exceção ParseError que ocorre ao acessar request.data com entrada malformada.
		


	# Juntando tudo

		# Ok, vamos em frente e começar a usar esses novos componentes para escrever algumas visualizações.

		# Não precisamos mais da nossa classe JSONResponse em views.py, então exclua-a. Feito isso, podemos começar a refatorar ligeiramente nossas visualizações.

			from rest_framework import status
			from rest_framework.decorators import api_view
			from rest_framework.response import Response
			from snippets.models import Snippet
			from snippets.serializers import SnippetSerializer


			@api_view(['GET', 'POST'])
			def snippet_list(request):
			    """
			    List all code snippets, or create a new snippet.
			    """
			    if request.method == 'GET':
			        snippets = Snippet.objects.all()
			        serializer = SnippetSerializer(snippets, many=True)
			        return Response(serializer.data)

			    elif request.method == 'POST':
			        serializer = SnippetSerializer(data=request.data)
			        if serializer.is_valid():
			            serializer.save()
			            return Response(serializer.data, status=status.HTTP_201_CREATED)
			        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


		# Nossa view de instância é uma melhoria em relação ao exemplo anterior. É um pouco mais conciso, e o código agora parece muito semelhante ao de estarmos trabalhando com a API de formulários. Também estamos usando códigos de status nomeados, o que torna os significados da resposta mais óbvios.

		# Aqui está a visualização de um snippet individual, no módulo views.py.

			@api_view(['GET', 'PUT', 'DELETE'])
			def snippet_detail(request, pk):
			    """
			    Retrieve, update or delete a code snippet.
			    """
			    try:
			        snippet = Snippet.objects.get(pk=pk)
			    except Snippet.DoesNotExist:
			        return Response(status=status.HTTP_404_NOT_FOUND)

			    if request.method == 'GET':
			        serializer = SnippetSerializer(snippet)
			        return Response(serializer.data)

			    elif request.method == 'PUT':
			        serializer = SnippetSerializer(snippet, data=request.data)
			        if serializer.is_valid():
			            serializer.save()
			            return Response(serializer.data)
			        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

			    elif request.method == 'DELETE':
			        snippet.delete()
			        return Response(status=status.HTTP_204_NO_CONTENT)



		# Tudo isso deve parecer muito familiar - não é muito diferente de trabalhar com views regulares do Django.

		# Observe que não estamos mais vinculando explicitamente nossas solicitações ou respostas a um determinado tipo de conteúdo. request.data pode lidar com solicitações json recebidas, mas também com outros formatos. Da mesma forma, estamos retornando objetos de resposta com dados, mas permitindo que a estrutura REST processe a resposta no tipo de conteúdo correto para nós.
		


	# Adicionando sufixos de formato opcional aos nossos URLs

		# Para aproveitar o fato de que nossas respostas não são mais conectadas a um único tipo de conteúdo, vamos adicionar suporte para sufixos de formato em nossos pontos de extremidade da API (API endpoints). O uso de sufixos de formato nos fornece URLs que se referem explicitamente a um determinado formato e significa que nossa API poderá lidar com URLs como http://example.com/api/items/4.json .

		# Comece adicionando um argumento de palavra-chave de format às duas visualizações, assim.

			def snippet_list(request, format=None):

		# e

			def snippet_detail(request, pk, format=None):



		# Agora atualize levemente o arquivo snippets/urls.py, para anexar um conjunto de format_suffix_patterns, além dos URLs existentes.

			from django.urls import path
			from rest_framework.urlpatterns import format_suffix_patterns
			from snippets import views

			urlpatterns = [
			    path('snippets/', views.snippet_list),
			    path('snippets/<int:pk>', views.snippet_detail),
			]

			urlpatterns = format_suffix_patterns(urlpatterns)



		# Não precisamos necessariamente adicionar esses padrões de URL extras, mas isso nos fornece uma maneira simples e limpa de nos referir a um formato específico.
		


	# Como está?

		# Vá em frente e teste a API na linha de comando, como fizemos no tutorial parte 1 . Tudo está funcionando da mesma maneira, embora tenhamos um tratamento melhor dos erros se enviarmos solicitações inválidas.

		# Podemos obter uma lista de todos os trechos, como antes.

			http http://127.0.0.1:8000/snippets/

			HTTP/1.1 200 OK
			...
			[
			  {
			    "id": 1,
			    "title": "",
			    "code": "foo = \"bar\"\n",
			    "linenos": false,
			    "language": "python",
			    "style": "friendly"
			  },
			  {
			    "id": 2,
			    "title": "",
			    "code": "print(\"hello, world\")\n",
			    "linenos": false,
			    "language": "python",
			    "style": "friendly"
			  }
			]


		# Podemos controlar o formato da resposta que recebemos de volta, usando o cabeçalho Accept :

			http http://127.0.0.1:8000/snippets/ Accept:application/json  # Request JSON
			http http://127.0.0.1:8000/snippets/ Accept:text/html         # Request HTML


		# Ou anexando um sufixo de formato:

			http http://127.0.0.1:8000/snippets.json  # JSON suffix
			http http://127.0.0.1:8000/snippets.api   # Browsable API suffix


			# tom
			http http://127.0.0.1:8000/snippets/4.json


		# Da mesma forma, podemos controlar o formato da solicitação que enviamos, usando o cabeçalho Content-Type .

			# POST using form data
			http --form POST http://127.0.0.1:8000/snippets/ code="print(123)"

			{
			  "id": 3,
			  "title": "",
			  "code": "print(123)",
			  "linenos": false,
			  "language": "python",
			  "style": "friendly"
			}

			# POST using JSON
			http --json POST http://127.0.0.1:8000/snippets/ code="print(456)"

			{
			    "id": 4,
			    "title": "",
			    "code": "print(456)",
			    "linenos": false,
			    "language": "python",
			    "style": "friendly"
			}


		# Se você adicionar uma opção --debug às solicitações http acima, poderá ver o tipo de solicitação nos cabeçalhos das solicitações.

		# Agora vá e abra a API em um navegador da Web, visitando http://127.0.0.1:8000/snippets/ .
		


	# Navegabilidade

		# Como a API escolhe o tipo de conteúdo da resposta com base na solicitação do cliente, ela retornará, por padrão, uma representação do recurso em formato HTML quando esse recurso for solicitado por um navegador da web. Isso permite que a API retorne uma representação HTML totalmente navegável na Web.

		# Ter uma API navegável na Web é uma grande vitória na usabilidade e facilita muito o desenvolvimento e o uso da API. Isso também reduz drasticamente a barreira de entrada para outros desenvolvedores que desejam inspecionar e trabalhar com sua API.

		# Consulte o tópico da API navegável para obter mais informações sobre o recurso da API navegável e como personalizá-lo.
		

	# Qual é o próximo?

		# Na parte 3 do tutorial, começaremos a usar visualizações baseadas em classe e veremos como as visualizações genéricas reduzem a quantidade de código que precisamos escrever. 




# ##############################################################################
# ##############################################################################
# ##############################################################################
# ##############################################################################
20-11-2019 22:05

	# 3 - Class based views - Django REST framework
	https://www.django-rest-framework.org/tutorial/3-class-based-views/


	# Tutorial 3: Visualizações baseadas em classe

		# Também podemos escrever nossas visualizações de API usando visualizações baseadas em classes, em vez de visualizações baseadas em funções. Como veremos, esse é um padrão poderoso que nos permite reutilizar funcionalidades comuns e nos ajuda a manter nosso código SECO .
	

	# Reescrevendo nossa API usando visualizações baseadas em classe

		# Começaremos reescrevendo a visualização raiz como uma visualização baseada em classe. Tudo isso envolve um pouco de refatoração do views.py .

			from snippets.models import Snippet
			from snippets.serializers import SnippetSerializer
			from django.http import Http404
			from rest_framework.views import APIView
			from rest_framework.response import Response
			from rest_framework import status


			class SnippetList(APIView):
			    """
			    List all snippets, or create a new snippet.
			    """
			    def get(self, request, format=None):
			        snippets = Snippet.objects.all()
			        serializer = SnippetSerializer(snippets, many=True)
			        return Response(serializer.data)

			    def post(self, request, format=None):
			        serializer = SnippetSerializer(data=request.data)
			        if serializer.is_valid():
			            serializer.save()
			            return Response(serializer.data, status=status.HTTP_201_CREATED)
			        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



		# Por enquanto, tudo bem. Parece bastante semelhante ao caso anterior, mas temos uma melhor separação entre os diferentes métodos HTTP. Também precisamos atualizar a exibição da instância em views.py .

			class SnippetDetail(APIView):
			    """
			    Retrieve, update or delete a snippet instance.
			    """
			    def get_object(self, pk):
			        try:
			            return Snippet.objects.get(pk=pk)
			        except Snippet.DoesNotExist:
			            raise Http404

			    def get(self, request, pk, format=None):
			        snippet = self.get_object(pk)
			        serializer = SnippetSerializer(snippet)
			        return Response(serializer.data)

			    def put(self, request, pk, format=None):
			        snippet = self.get_object(pk)
			        serializer = SnippetSerializer(snippet, data=request.data)
			        if serializer.is_valid():
			            serializer.save()
			            return Response(serializer.data)
			        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

			    def delete(self, request, pk, format=None):
			        snippet = self.get_object(pk)
			        snippet.delete()
			        return Response(status=status.HTTP_204_NO_CONTENT)



		# Isso parece bom. Novamente, ainda é bastante semelhante à view baseada em funções no momento.

		# Também precisamos refatorar nossos snippets/urls.py agora que estamos usando visualizações baseadas em classe.

			from django.urls import path
			from rest_framework.urlpatterns import format_suffix_patterns
			from snippets import views

			urlpatterns = [
			    path('snippets/', views.SnippetList.as_view()),
			    path('snippets/<int:pk>/', views.SnippetDetail.as_view()),
			]

			urlpatterns = format_suffix_patterns(urlpatterns)


		# Ok, terminamos. Se você executar o servidor de desenvolvimento, tudo deverá estar funcionando como antes.
		

	# Usando mixins

		# Uma das grandes vitórias do uso de views baseadas em classe é que ela permite compor com facilidade pedaços de comportamento reutilizáveis.

		# As operações de criação / recuperação / atualização / exclusão que usamos até agora serão bastante semelhantes para todas as views de API suportadas pelo modelo que criamos. Esses bits de comportamento comum são implementados nas classes mixin da estrutura REST.

		# Vamos dar uma olhada em como podemos compor as views usando as classes mixin. Aqui está o nosso módulo views.py novamente.

			from snippets.models import Snippet
			from snippets.serializers import SnippetSerializer
			from rest_framework import mixins
			from rest_framework import generics

			class SnippetList(mixins.ListModelMixin,
			                  mixins.CreateModelMixin,
			                  generics.GenericAPIView):
			    queryset = Snippet.objects.all()
			    serializer_class = SnippetSerializer

			    def get(self, request, *args, **kwargs):
			        return self.list(request, *args, **kwargs)

			    def post(self, request, *args, **kwargs):
			        return self.create(request, *args, **kwargs)



		# Tomaremos um momento para examinar exatamente o que está acontecendo aqui. Estamos construindo nossa view usando GenericAPIView e adicionando ListModelMixin e CreateModelMixin .

		# A classe base fornece a funcionalidade principal e as classes mixin fornecem as .list() e .create(). Em seguida, vinculamos explicitamente os métodos get e post às ações apropriadas. Coisas simples o suficiente até agora.

			class SnippetDetail(mixins.RetrieveModelMixin,
			                    mixins.UpdateModelMixin,
			                    mixins.DestroyModelMixin,
			                    generics.GenericAPIView):
			    queryset = Snippet.objects.all()
			    serializer_class = SnippetSerializer

			    def get(self, request, *args, **kwargs):
			        return self.retrieve(request, *args, **kwargs)

			    def put(self, request, *args, **kwargs):
			        return self.update(request, *args, **kwargs)

			    def delete(self, request, *args, **kwargs):
			        return self.destroy(request, *args, **kwargs)


		# Muito similar. Novamente, estamos usando a classe GenericAPIView para fornecer a funcionalidade principal e adicionando mixins para fornecer as .retrieve() , .update() e .destroy() .

		# tom
			http --json POST http://127.0.0.1:8000/snippets/ code="print(987)"

			http http://127.0.0.1:8000/snippets/6.json



	# Usando views genéricas baseadas em classe

		# Usando as classes mixin, reescrevemos as views para usar um pouco menos de código do que antes, mas podemos dar um passo adiante. A estrutura REST fornece um conjunto de views genéricas já misturadas que podemos usar para reduzir ainda mais nosso módulo views.py .

			from snippets.models import Snippet
			from snippets.serializers import SnippetSerializer
			from rest_framework import generics


			class SnippetList(generics.ListCreateAPIView):
			    queryset = Snippet.objects.all()
			    serializer_class = SnippetSerializer


			class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
			    queryset = Snippet.objects.all()
			    serializer_class = SnippetSerializer



		# Uau, isso é bastante conciso. Recebemos uma quantidade enorme de graça, e nosso código parece um Django bom, limpo e idiomático.

		# Em seguida, passaremos para a parte 4 do tutorial , onde veremos como podemos lidar com autenticação e permissões para nossa API. 



21-11-2019 00:07


# ##############################################################################
# ##############################################################################
# ##############################################################################
# ##############################################################################
21-11-2019 00:07

	# 4 - Authentication and permissions - Django REST framework
	https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/


	# Tutorial 4: Autenticação e permissões


	# Atualmente, nossa API não possui restrições sobre quem pode editar ou excluir trechos de código. Gostaríamos de ter um comportamento mais avançado para garantir que:

	    # Os trechos de código são sempre associados a um criador.
	    # Somente usuários autenticados podem criar trechos.
	    # Somente o criador de um trecho pode atualizá-lo ou excluí-lo.
	    # Solicitações não autenticadas devem ter acesso total somente leitura. 



	# Adicionando informações ao nosso modelo

		# Vamos fazer algumas alterações em nossa classe de modelo de Snippet . Primeiro, vamos adicionar alguns campos. Um desses campos será usado para representar o usuário que criou o snippet de código. O outro campo será usado para armazenar a representação HTML destacada do código.

		# Adicione os dois campos a seguir ao modelo de Snippet em models.py.

			owner = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE)
			highlighted = models.TextField()



		# Também precisamos garantir que, quando o modelo for salvo, preencha o campo highlighted, usando a biblioteca de destaque do código de pygments.

		# Vamos precisar de algumas importações extras:

			from pygments.lexers import get_lexer_by_name
			from pygments.formatters.html import HtmlFormatter
			from pygments import highlight



		# E agora podemos adicionar um método .save() à nossa classe de modelo:

			def save(self, *args, **kwargs):
			    """
			    Use the `pygments` library to create a highlighted HTML
			    representation of the code snippet.
			    """
			    lexer = get_lexer_by_name(self.language)
			    linenos = 'table' if self.linenos else False
			    options = {'title': self.title} if self.title else {}
			    formatter = HtmlFormatter(style=self.style, linenos=linenos,
			                              full=True, **options)
			    self.highlighted = highlight(self.code, lexer, formatter)
			    super(Snippet, self).save(*args, **kwargs)



		# Quando tudo estiver pronto, precisaremos atualizar nossas tabelas de banco de dados. Normalmente, criaríamos uma migração de banco de dados para fazer isso, mas, para os propósitos deste tutorial, vamos excluir o banco de dados e começar novamente.

			rm -f db.sqlite3
			rm -r snippets/migrations
			python manage.py makemigrations snippets
			python manage.py migrate



		# Você também pode criar alguns usuários diferentes, para usar no teste da API. A maneira mais rápida de fazer isso será com o comando createsuperuser .

			python manage.py createsuperuser



	# Adicionando terminais (endpoints) para nossos modelos de usuário

		# Agora que temos alguns usuários com quem trabalhar, é melhor adicionar representações desses usuários à nossa API. Criar um novo serializador é fácil. Em serializers.py adicione:

			from django.contrib.auth.models import User

			class UserSerializer(serializers.ModelSerializer):
			    snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())

			    class Meta:
			        model = User
			        fields = ['id', 'username', 'snippets']



		# Como 'snippets' é um relacionamento inverso no modelo de Usuário, ele não será incluído por padrão ao usar a classe ModelSerializer, portanto, precisamos adicionar um campo explícito para ele.

		# Também adicionaremos algumas visualizações ao views.py. Gostaríamos de usar apenas views somente leitura para as representações do usuário, portanto, usaremos as views genéricas baseadas em classe ListAPIView e RetrieveAPIView .

			from django.contrib.auth.models import User


			class UserList(generics.ListAPIView):
			    queryset = User.objects.all()
			    serializer_class = UserSerializer


			class UserDetail(generics.RetrieveAPIView):
			    queryset = User.objects.all()
			    serializer_class = UserSerializer



		# Certifique-se de também importar a classe UserSerializer

			from snippets.serializers import UserSerializer


		# Finalmente, precisamos adicionar essas visualizações à API, referenciando-as a partir da URL conf. Adicione o seguinte aos padrões em snippets/urls.py

			path('users/', views.UserList.as_view()),
			path('users/<int:pk>/', views.UserDetail.as_view()),




	# Associando snippets a usuários

		# No momento, se criamos um trecho de código, não há como associar o usuário que criou o snippet, à instância do snippet. O usuário não é enviado como parte da representação serializada, mas é uma propriedade da solicitação recebida.

		# A maneira como lidamos com isso é substituindo um método .perform_create() em nossas views de snippet, que nos permite modificar como o salvamento da instância é gerenciado e manipular qualquer informação implícita na solicitação de entrada ou no URL solicitado.

		# Na classe de exibição SnippetList, adicione o seguinte método:

			def perform_create(self, serializer):
			    serializer.save(owner=self.request.user)


		# O método create() do nosso serializador agora receberá um campo 'owner' adicional, juntamente com os dados validados da solicitação.


	# Atualizando nosso serializador

		# Agora que os snippets estão associados ao usuário que os criou, vamos atualizar nosso SnippetSerializer para refletir isso. Adicione o seguinte campo à definição de serializers.py em serializers.py :

			owner = serializers.ReadOnlyField(source='owner.username')


		# Nota : Certifique-se de adicionar também 'owner', à lista de campos na classe Meta interna.

		# Este campo está fazendo algo bastante interessante. O argumento de source controla qual atributo é usado para preencher um campo e pode apontar para qualquer atributo na instância serializada. Também pode usar a notação pontilhada mostrada acima; nesse caso, ele percorrerá os atributos fornecidos, de maneira semelhante à usada na linguagem de modelos do Django.

		# O campo que adicionamos é a classe ReadOnlyField, em contraste com os outros campos digitados, como CharField, BooleanField etc ... O ReadOnlyField é sempre somente leitura e será usado para representações serializadas, mas não será usado para atualizar instâncias do modelo quando elas são desserializadas. Também poderíamos ter usado CharField(read_only=True) aqui.


	# Adicionando permissões necessárias às visualizações

		# Agora que os snippets de código estão associados aos usuários, queremos garantir que apenas usuários autenticados possam criar, atualizar e excluir snippets de código.

		# A estrutura REST inclui várias classes de permissão que podemos usar para restringir quem pode acessar uma determinada exibição. Nesse caso, o que procuramos é IsAuthenticatedOrReadOnly , que garantirá que solicitações autenticadas obtenham acesso de leitura e gravação e solicitações não autenticadas obtenham acesso somente leitura.

		# Primeiro, adicione a seguinte importação no módulo de views

			from rest_framework import permissions


		# Em seguida, adicione a seguinte propriedade às classes de exibição SnippetList e SnippetDetail.

			permission_classes = [permissions.IsAuthenticatedOrReadOnly]



	# Adicionando login à API Navegável

		# Se você abrir um navegador e navegar para a API navegável no momento, descobrirá que não poderá mais criar novos trechos de código. Para fazer isso, precisaríamos fazer o login como usuário.

		# Podemos adicionar uma view de login para uso com a API navegável, editando o URLconf em nosso arquivo urls.py nível do projeto.

		# Adicione a seguinte importação na parte superior do arquivo:

			from django.conf.urls import include


		# E, no final do arquivo, adicione um padrão para incluir as visualizações de logon e logout da API navegável.

			urlpatterns += [
			    path('api-auth/', include('rest_framework.urls')),
			]


		# A parte 'api-auth/' do padrão pode realmente ser o URL que você deseja usar.

		# Agora, se você abrir o navegador novamente e atualizar a página, verá um link 'Login' no canto superior direito da página. Se você fizer login como um dos usuários criados anteriormente, poderá criar trechos de código novamente.

		# Depois de criar alguns trechos de código, navegue até o terminal '/users/' e observe que a representação inclui uma lista dos IDs de snippet associados a cada usuário, no campo 'snippet' de cada usuário.
		

		# tom
		http://127.0.0.1:8000/snippets/
		http://127.0.0.1:8000/users/



	# Permissões no nível do objeto

		# Realmente, gostaríamos que todos os trechos de código estivessem visíveis para qualquer pessoa, mas também certifique-se de que apenas o usuário que criou um trecho de código possa atualizá-lo ou excluí-lo.

		# Para fazer isso, precisamos criar uma permissão personalizada.

		# No aplicativo de snippets, crie um novo arquivo, permissions.py

			from rest_framework import permissions


			class IsOwnerOrReadOnly(permissions.BasePermission):
			    """
			    Custom permission to only allow owners of an object to edit it.
			    """

			    def has_object_permission(self, request, view, obj):
			        # Read permissions are allowed to any request,
			        # so we'll always allow GET, HEAD or OPTIONS requests.
			        if request.method in permissions.SAFE_METHODS:
			            return True

			        # Write permissions are only allowed to the owner of the snippet.
			        return obj.owner == request.user



		# Agora podemos adicionar essa permissão personalizada ao nosso ponto de extremidade da instância de snippet, editando a propriedade permission_classes na classe de exibição SnippetDetail:

			permission_classes = [permissions.IsAuthenticatedOrReadOnly,
			                      IsOwnerOrReadOnly]


		# Certifique-se de também importar a classe IsOwnerOrReadOnly .

			from snippets.permissions import IsOwnerOrReadOnly


		# Agora, se você abrir um navegador novamente, verá que as ações 'DELETE' e 'PUT' aparecerão apenas em um ponto de extremidade da instância de trecho se você estiver conectado como o mesmo usuário que criou o trecho de código.
		

		# tom
		http://127.0.0.1:8000/snippets/1/
			# HTTP 200 OK
			# Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS



	# Autenticando com a API

		# Como agora temos um conjunto de permissões na API, precisamos autenticar nossas solicitações para isso, se quisermos editar snippets. Como não configuramos nenhuma classe de autenticação , os padrões atualmente são aplicados, como SessionAuthentication e BasicAuthentication .

		# Quando interagimos com a API por meio do navegador da Web, podemos efetuar login e a sessão do navegador fornecerá a autenticação necessária para as solicitações.

		# Se estivermos interagindo com a API programaticamente, precisamos fornecer explicitamente as credenciais de autenticação em cada solicitação.

		# Se tentarmos criar um trecho sem autenticação, receberemos um erro:

			http POST http://127.0.0.1:8000/snippets/ code="print(123)"

			{
			    "detail": "Authentication credentials were not provided."
			}


		# Podemos fazer uma solicitação bem-sucedida incluindo o nome e a senha de um dos usuários que criamos anteriormente.

			http -a admin:password123 POST http://127.0.0.1:8000/snippets/ code="print(789)"

			{
			    "id": 1,
			    "owner": "admin",
			    "title": "foo",
			    "code": "print(789)",
			    "linenos": false,
			    "language": "python",
			    "style": "friendly"
			}


			# tom
			http -a admin:adminadmin POST http://127.0.0.1:8000/snippets/ code="print(789)"

			http -a tomaz:tomaztomaz POST http://127.0.0.1:8000/snippets/1 code="print(editado)"

			# Não fuincionou, deve ser o formato da url
			# testando edição em um item criado por outro usuário
			http -a tomaz:tomaztomaz PUT http://127.0.0.1:8000/snippets/1 code="print(editado)"

				# HTTP/1.1 500 Internal Server Error
				# Connection: close

			http -a tomaz:tomaztomaz PUT http://127.0.0.1:8000/snippets/4 code="print(editado)"


			# Na versão html, é possível visualizar o botão DELETE quando o item pertence ao usuário.


			# ------------------------------------------------------------------------------

			# ok
			http -a admin:adminadmin POST http://127.0.0.1:8000/snippets/ code="ls -la"
				# HTTP/1.1 201 Created
				# Allow: GET, POST, HEAD, OPTIONS


			http -a admin:adminadmin DELETE http://127.0.0.1:8000/snippets/5
				# HTTP/1.1 301 Moved Permanently
				# Content-Length: 0

			# ok
			http http://127.0.0.1:8000/snippets/   			

			# ok
			http http://127.0.0.1:8000/snippets/4.json


			http --json POST http://127.0.0.1:8000/snippets/ code="print(987)"

			http http://127.0.0.1:8000/snippets/6.json


	# Sumário

	# Agora, temos um conjunto de permissões bastante refinado em nossa API da Web e pontos finais (end points) para os usuários do sistema e para os trechos de código que eles criaram.

	# Na parte 5 do tutorial, veremos como podemos unir tudo criando um ponto de extremidade HTML para nossos trechos destacados e melhorando a coesão de nossa API usando hiperlink para os relacionamentos dentro do sistema. 






# ##############################################################################
# ##############################################################################
# ##############################################################################
# ##############################################################################
22-11-2019 20:55

	# 5 - Relationships and hyperlinked APIs - Django REST framework
	https://www.django-rest-framework.org/tutorial/5-relationships-and-hyperlinked-apis/


	# Tutorial 5: Relacionamentos e APIs com hiperlink

		# No momento, os relacionamentos em nossa API são representados usando chaves primárias. Nesta parte do tutorial, melhoraremos a coesão e a capacidade de descoberta de nossa API, usando o hiperlink para relacionamentos.
		

	# Criando um nó de extremidade para a raiz da nossa API

		# No momento, temos pontos finais (endpoints) para 'snippets' e 'users', mas não temos um único ponto de entrada para nossa API. Para criar uma, usaremos uma exibição regular baseada em funções e o decorador @api_view que introduzimos anteriormente. Nos seus snippets/views.py adicione:

			from rest_framework.decorators import api_view
			from rest_framework.response import Response
			from rest_framework.reverse import reverse


			@api_view(['GET'])
			def api_root(request, format=None):
			    return Response({
			        'users': reverse('user-list', request=request, format=format),
			        'snippets': reverse('snippet-list', request=request, format=format)
			    })



		# Duas coisas devem ser notadas aqui. Primeiro, estamos usando a função reverse da estrutura REST para retornar URLs totalmente qualificados; segundo, os padrões de URL são identificados por nomes de conveniência que declararemos posteriormente em nossos snippets/urls.py


	# Criando um nó de extremidade (endpoints) para os trechos destacados

		# A outra coisa óbvia que ainda falta na nossa API pastebin é o código que destaca os pontos de extremidade (endpoints).

		# Diferentemente de todos os outros pontos de extremidade (endpoints) da API, não queremos usar JSON, mas apenas apresentar uma representação HTML. Existem dois estilos de renderizador de HTML fornecidos pela estrutura REST, um para lidar com HTML renderizado usando modelos, o outro para lidar com HTML pré-renderizado. O segundo renderizador é o que gostaríamos de usar para esse terminal.

		# A outra coisa que precisamos considerar ao criar a visualização de destaque do código é que não há uma visualização genérica concreta existente que possamos usar. Não estamos retornando uma instância de objeto, mas sim uma propriedade de uma instância de objeto.

		# Em vez de usar uma view genérica concreta, usaremos a classe base para representar instâncias e criaremos nosso próprio método .get() . Nos seus snippets/views.py adicione:

			from rest_framework import renderers
			from rest_framework.response import Response

			class SnippetHighlight(generics.GenericAPIView):
			    queryset = Snippet.objects.all()
			    renderer_classes = [renderers.StaticHTMLRenderer]

			    def get(self, request, *args, **kwargs):
			        snippet = self.get_object()
			        return Response(snippet.highlighted)


		# Como sempre, precisamos adicionar as novas views que criamos no nosso URLconf. Adicionaremos um padrão de URL para nossa nova raiz de API em snippets/urls.py :

			path('', views.api_root),


		# E adicione um padrão de URL para os destaques do snippet:

			path('snippets/<int:pk>/highlight/', views.SnippetHighlight.as_view()),


			# tom
			http://127.0.0.1:8000/snippets/1/highlight/
			http://127.0.0.1:8000/users.json



	# Hiperligando nossa API

		# Lidar com relacionamentos entre entidades é um dos aspectos mais desafiadores do design da API da Web. Existem várias maneiras diferentes que podemos escolher para representar um relacionamento:

		    # Usando chaves primárias.
		    # Usando hiperlink entre entidades.
		    # Usando um campo de lesma(slug) de identificação exclusivo na entidade relacionada.
		    # Usando a representação de sequência padrão da entidade relacionada.
		    # Aninhando a entidade relacionada dentro da representação pai.
		    # Alguma outra representação personalizada. 

		# A estrutura REST suporta todos esses estilos e pode aplicá-los a relacionamentos avançados ou reversos ou a aplicá-los a gerenciadores personalizados, como chaves estrangeiras genéricas.

		# Nesse caso, gostaríamos de usar um estilo de hiperlink entre entidades. Para isso, modificaremos nossos serializadores para estender o HyperlinkedModelSerializer vez do ModelSerializer existente.

		# O HyperlinkedModelSerializer possui as seguintes diferenças do ModelSerializer :

		    # Ele não inclui o campo de id por padrão.
		    # Ele inclui um campo de url , usando HyperlinkedIdentityField .
		    # Os relacionamentos usam HyperlinkedRelatedField , em vez de PrimaryKeyRelatedField . 

		# Podemos facilmente reescrever nossos serializadores existentes para usar hiperlinks. Nos seus snippets/serializers.py adicione:

			class SnippetSerializer(serializers.HyperlinkedModelSerializer):
			    owner = serializers.ReadOnlyField(source='owner.username')
			    highlight = serializers.HyperlinkedIdentityField(view_name='snippet-highlight', format='html')

			    class Meta:
			        model = Snippet
			        fields = ['url', 'id', 'highlight', 'owner',
			                  'title', 'code', 'linenos', 'language', 'style']


			class UserSerializer(serializers.HyperlinkedModelSerializer):
			    snippets = serializers.HyperlinkedRelatedField(many=True, view_name='snippet-detail', read_only=True)

			    class Meta:
			        model = User
			        fields = ['url', 'id', 'username', 'snippets']



		# Observe que também adicionamos um novo campo 'highlight' . Esse campo é do mesmo tipo que o campo de url , exceto pelo fato de apontar para o padrão de URL 'snippet-highlight' , em vez do padrão de URL 'snippet-detail' .

		# Como incluímos URLs com sufixo de formato, como '.json' , também precisamos indicar no campo de highlight que qualquer hiperlink com sufixo de formato retornado deve usar o sufixo '.html' .
		


	# Certificando-se de que nossos padrões de URL sejam nomeados

		# Se quisermos ter uma API com hiperlink, precisamos nos certificar de nomear nossos padrões de URL. Vamos dar uma olhada em quais padrões de URL precisamos nomear.

		    # A raiz da nossa API refere-se a 'user-list' e 'snippet-list' .
		    # Nosso serializador de trechos inclui um campo que se refere a 'snippet-highlight' .
		    # Nosso serializador de usuário inclui um campo que se refere a 'snippet-detail' .
		    # Nossos serializadores de snippet e usuário incluem campos 'url' que, por padrão, se referem a '{model_name}-detail' , que nesse caso serão 'snippet-detail' e 'user-detail' . 

		# Após adicionar todos esses nomes ao nosso URLconf, nosso arquivo snippets/urls.py final deve ficar assim:
		from django.urls import path
		from rest_framework.urlpatterns import format_suffix_patterns
		from snippets import views

		# API endpoints
		urlpatterns = format_suffix_patterns([
		    path('', views.api_root),
		    path('snippets/',
		        views.SnippetList.as_view(),
		        name='snippet-list'),
		    path('snippets/<int:pk>/',
		        views.SnippetDetail.as_view(),
		        name='snippet-detail'),
		    path('snippets/<int:pk>/highlight/',
		        views.SnippetHighlight.as_view(),
		        name='snippet-highlight'),
		    path('users/',
		        views.UserList.as_view(),
		        name='user-list'),
		    path('users/<int:pk>/',
		        views.UserDetail.as_view(),
		        name='user-detail')
		])



	# Adicionando paginação

	# As exibições de lista para usuários e trechos de código podem retornar muitas instâncias. Por isso, gostaríamos de garantir a paginação dos resultados e permitir que o cliente da API percorra cada uma das páginas individuais.

	# Podemos alterar o estilo da lista padrão para usar a paginação, modificando um pouco o arquivo tutorial/settings.py . Adicione a seguinte configuração:

		REST_FRAMEWORK = {
		    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
		    'PAGE_SIZE': 10
		}


	# Observe que as configurações na estrutura REST estão todas com espaço para nome em uma única configuração de dicionário, denominada REST_FRAMEWORK , que ajuda a mantê-las bem separadas das outras configurações do projeto.

	# Também poderíamos personalizar o estilo de paginação se precisássemos também, mas, neste caso, continuaremos com o padrão.
	


	# Navegando na API

		# Se abrirmos um navegador e navegarmos para a API navegável, você descobrirá que agora pode contornar a API simplesmente seguindo os links.

		# Você também poderá ver os links 'realçar' nas instâncias de snippet, que o levarão às representações HTML do código destacado.

	# Na parte 6 do tutorial, veremos como podemos usar os ViewSets e os roteadores para reduzir a quantidade de código necessária para criar nossa API. 




# ##############################################################################
# ##############################################################################
# ##############################################################################
# ##############################################################################
23-11-2019 02:35

	# 6 - Viewsets and routers - Django REST framework
	https://www.django-rest-framework.org/tutorial/6-viewsets-and-routers/

	
	# Tutorial 6: ViewSets e roteadores

		# A estrutura REST inclui uma abstração para lidar com os ViewSets , que permite ao desenvolvedor se concentrar na modelagem do estado e das interações da API e deixa a construção da URL ser tratada automaticamente, com base em convenções comuns.

		# Classes ViewSet são quase a mesma coisa que as classes View , exceto que elas fornecem operações como read ou update e não manipuladores de métodos, como get ou put .

		# Uma classe ViewSet é vinculada apenas a um conjunto de manipuladores de métodos no último momento, quando é instanciada em um conjunto de exibições, geralmente usando uma classe Router que lida com as complexidades de definir a configuração de URL para você.



	# Refatorando para usar ViewSets

		# Vamos pegar nosso conjunto de views atual e refatorá-los em view sets.

		# Primeiro, refatoremos nossas views UserList e UserDetail em um único UserViewSet. Podemos remover as duas visualizações e substituí-las por uma única classe:

			from rest_framework import viewsets

			class UserViewSet(viewsets.ReadOnlyModelViewSet):
			    """
			    This viewset automatically provides `list` and `detail` actions.
			    """
			    queryset = User.objects.all()
			    serializer_class = UserSerializer



		# Aqui, usamos a classe ReadOnlyModelViewSet para fornecer automaticamente as operações padrão 'somente leitura'. Ainda estamos definindo os atributos queryset e serializer_class exatamente como fizemos quando estávamos usando visualizações regulares, mas não precisamos mais fornecer as mesmas informações para duas classes separadas.

		# Em seguida, substituiremos as classes de exibição SnippetList , SnippetDetail e SnippetHighlight . Podemos remover as três visualizações e substituí-las novamente por uma única classe.

			from rest_framework.decorators import action
			from rest_framework.response import Response

			class SnippetViewSet(viewsets.ModelViewSet):
			    """
			    This viewset automatically provides `list`, `create`, `retrieve`,
			    `update` and `destroy` actions.

			    Additionally we also provide an extra `highlight` action.
			    """
			    queryset = Snippet.objects.all()
			    serializer_class = SnippetSerializer
			    permission_classes = [permissions.IsAuthenticatedOrReadOnly,
			                          IsOwnerOrReadOnly]

			    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
			    def highlight(self, request, *args, **kwargs):
			        snippet = self.get_object()
			        return Response(snippet.highlighted)

			    def perform_create(self, serializer):
			        serializer.save(owner=self.request.user)


		# Desta vez, usamos a classe ModelViewSet para obter o conjunto completo de operações padrão de leitura e gravação.

		# Observe que também usamos o decorator @action para criar uma ação personalizada, chamada de highlight. Este decorador pode ser usado para adicionar pontos de extremidade personalizados que não se encaixam no estilo padrão de create / update / delete .

		# As ações personalizadas que usam o decorador @action responderão às solicitações GET por padrão. Podemos usar o argumento method se quisermos uma ação que responda às solicitações POST .

		# Os URLs para ações personalizadas, por padrão, dependem do próprio nome do método. Se você quiser alterar a maneira como o URL deve ser construído, inclua url_path como argumento da palavra-chave do decorador.
		


	# Vinculando ViewSets a URLs explicitamente

		# Os métodos manipuladores só ficam vinculados às ações quando definimos o URLConf. Para ver o que está acontecendo, vamos primeiro criar explicitamente um conjunto de views em nossos ViewSets.

		# No arquivo snippets/urls.py , vinculamos nossas classes ViewSet a um conjunto de views concretas.

			from snippets.views import SnippetViewSet, UserViewSet, api_root
			from rest_framework import renderers

			snippet_list = SnippetViewSet.as_view({
			    'get': 'list',
			    'post': 'create'
			})
			snippet_detail = SnippetViewSet.as_view({
			    'get': 'retrieve',
			    'put': 'update',
			    'patch': 'partial_update',
			    'delete': 'destroy'
			})
			snippet_highlight = SnippetViewSet.as_view({
			    'get': 'highlight'
			}, renderer_classes=[renderers.StaticHTMLRenderer])
			user_list = UserViewSet.as_view({
			    'get': 'list'
			})
			user_detail = UserViewSet.as_view({
			    'get': 'retrieve'


		# Observe como estamos criando várias views de cada classe ViewSet , vinculando os métodos http à ação necessária para cada visualização.

		# Agora que vinculamos nossos recursos a views concretas, podemos registrar as views com a URL conf, como de costume.

			urlpatterns = format_suffix_patterns([
			    path('', api_root),
			    path('snippets/', snippet_list, name='snippet-list'),
			    path('snippets/<int:pk>/', snippet_detail, name='snippet-detail'),
			    path('snippets/<int:pk>/highlight/', snippet_highlight, name='snippet-highlight'),
			    path('users/', user_list, name='user-list'),
			    path('users/<int:pk>/', user_detail, name='user-detail')
			])



	# Usando roteadores

		# Como estamos usando classes ViewSet vez de classes View , na verdade não precisamos projetar a URL conf. As convenções para conectar recursos a views e URLs podem ser tratadas automaticamente, usando uma classe Router . Tudo o que precisamos fazer é registrar os conjuntos de exibição apropriados em um roteador e deixar o resto.

		# Aqui está o nosso arquivo de snippets/urls.py reconectado.

			from django.urls import path, include
			from rest_framework.routers import DefaultRouter
			from snippets import views

			# Create a router and register our viewsets with it.
			router = DefaultRouter()
			router.register(r'snippets', views.SnippetViewSet)
			router.register(r'users', views.UserViewSet)

			# The API URLs are now determined automatically by the router.
			urlpatterns = [
			    path('', include(router.urls)),
			]


		# O registro dos conjuntos de views no roteador é semelhante a fornecer um padrão de URL. Incluímos dois argumentos - o prefixo da URL para as views e o próprio conjunto de views.

		# A classe DefaultRouter que estamos usando também cria automaticamente a visualização raiz da API para nós, para que agora possamos excluir o método api_root do nosso módulo de views .
	


	# Compensações entre views e views

		# Usar views pode ser uma abstração realmente útil. Isso ajuda a garantir que as convenções de URL sejam consistentes em sua API, minimiza a quantidade de código que você precisa escrever e permite que você se concentre nas interações e representações que sua API fornece, em vez das especificidades do URL conf.

		# Isso não significa que é sempre a abordagem correta a ser adotada. Há um conjunto semelhante de trade-offs a serem considerados como ao usar views baseadas em classe em vez de views baseadas em função. O uso de conjuntos de views é menos explícito do que criar suas views individualmente. 