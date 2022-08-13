# Baixe meu aplicativo de noticias:
# https://play.google.com/store/apps/details?id=com.canalfs0ciety.boletimtec

# Apoie meu Projeto de divulgação de noticias
# https://apoia.se/samirnews

from __future__ import print_function
import sys
from oauth2client import client
from googleapiclient import sample_tools
from googletrans import Translator
import requests
from bs4 import BeautifulSoup as Soup
import tweepy
import facebook
import time
import json

# Digite a Url do site no qual voce quer pegar a noticia
url_bleepcomputer = 'https://www.bleepingcomputer.com'

# Digite a Url do seu blog no Blogger
url_noticias_postadas = 'https://www.canalfsociety.com/'

#Como esse codigo é para pegar noticias de um site com noticias em ingles, vou usar a Api do Google Tradutor
translator = Translator(service_urls=['translate.googleapis.com'])
translator = Translator()

# É necessario criar um arquivo json com as credenciais, essas credenciais é de acordo com cada plataforma que voce vai usar
# No caso eu criei para 6 plataformas, se voce for usar todas vai ser preciso ver como pegar de cada uma delas
with open('credenciais.json', 'r') as json_file:
    dados = json.load(json_file)
# Aqui vai salvar cada informação de credencial em uma variavel
for item in dados:
    # Id do seu blogger, ela fica na url quando voce acessa o site para postar noticias 
    id_do_blogger = (item['blogger_id'])
    # Vai retornar o token do seu bot do telegram, voce consegue ele pelo father_bot
    telegram_bot_token = (item['telegram_bot_token'])
    # Retorna o chat_id do grupo/canal onde o bot foi adicionado, pegue ela pela url:
    # https://api.telegram.org/botSEU_TOKEN/getUpdates
    chat_id = (item['chat_id'])
    # Para pegar essas infomações do twitter recomendo ver algum video, pois fica mais facil o entendimento
    twitter_consumer_key = (item['consumer_key'])
    twitter_consumer_secret = (item['consumer_secret'])
    twitter_access_token = (item['access_token'])
    twitter_access_token_secret = (item['access_token_secret'])
    # Tambem recomendo ver algum video para pegar essas informaçoes do facebook
    token_do_facebook = (item['facetoken'])
    id_facebook = (item['id_facebook'])
    # Aqui retorna o token do Discord, recomendo tambem ver algum video explicativo
    token_discord = (item['authorization'])
    # Aqui retorna as credenciais do Instagram, tambem recomendo ver algum video
    id_do_instagram = (item['ig_user_id'])
    token_instagram = (item['insta_token'])

class DivulgaNoticias:
    def main(self):
        noticia_bleep = self.titulo_para_comparar()
        # Vai ver se a noticia ja foi postada, caso ja foi, ele retorna a seguinte mensagem
        if noticia_bleep == True:
            print ("Noticia ja postada")
        else:
            # Caso a noticia for nova, ele chama a função de postar no seu Blog
            self.postar_blogger(sys.argv)
            # Tambem chama a função de divulgar a noticia
            self.divulga_post()
            print ("Finalizado o Bot")
        # Aqui o bot vai esperar 20 minutos para buscar uma nova noticia    
        time.sleep(1200)
        
    # Eu mostro dois jeitos de fazer Web Scraping, o primeiro utilizado para pegar o link e o segundo pra pegar o restante das informações
    # Como aprendi das duas formas, achei interessante mostrar elas.
    
    # Aqui sera feito um Web Scraping na pagina principal do site para pegar o link da noticia que esta no topo
    def pegar_link(self):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0'}
        r = requests.get(url_bleepcomputer, headers=headers)
        html = Soup(r.text, 'html.parser')
        for ir_noticia in html.select('.bc_latest_news'):
            link_noticia = ir_noticia.select_one('.bc_latest_news_text').find('h4').find('a').get('href')
        return link_noticia

    # Agora vai pegar as informações que eu quero para postar a noticia no meu blog
    def pegar_noticia(self):
        link = self.pegar_link()
        # Primeiro é verificado se o link é de uma propaganda (especifico para esse site)
        l = ('offer/deals')
        if l in link:
            return True
        else:
            # Caso nao for propaganda, serão salvos as seguintes informaçoes na variavel informacoes_capturadas: titulo, imagem, texto, link e url 
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0'}
            r = requests.get(link, headers=headers)
            content = Soup(r.text, 'html.parser')
            image_class = 'articleBody'
            cards = content.find_all('div', {'class': 'article_section'})
            informacoes_capturadas = []
            for card in cards:
                informacoes_capturadas.append({
                    'titulo': card.find('h1').text,
                    'imagem': card.find('div', class_= image_class).find('img').get('src'),
                    'texto': card.find('div', class_= image_class).text,
                    'link': link,
                    'url': url_bleepcomputer,
                    })
            return informacoes_capturadas

    # Função que verifica se a noticia ja foi postada para que nao fique repetindo
    def titulo_para_comparar(self):
        titulo_novo = self.pegar_noticia()
        # Primeiro ele confirma se é propaganda
        if titulo_novo == True:
            print ("Propaganda")
            return True
        else:
            # Caso nao seja propaganda, vai comparar esse novo titulo com os titulos que estão na pagina principal do meu blog, se for igual, vai retornar True 
            for item in titulo_novo:
                titulo = (item['titulo'])
                # Vai ser traduzido o titulo e deixa-lo em maiusculo para ficar no mesmo formato com o ja postado
                titulo_traduzido = translator.translate(titulo, dest='pt').text
                titulo_noticia = (titulo_traduzido.upper())
            # É feito um Web Scraping no meu blog para pegar os titulos das noticias que estão na pagina principal    
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0'}
            r = requests.get(url_noticias_postadas, headers=headers)
            html = Soup(r.text, 'html.parser')
            for ir_noticia in html.select('.hentry'):
                titulo_postado = ir_noticia.select_one('.entry-title').text
                # Se o titulo que foi capturado for igual algum ja postado, ira retornar True
                if titulo_noticia in titulo_postado:
                    return True

    # Hora de fazer a postagem no Blogger 
    def postar_blogger(self,argv):
        postar = self.pegar_noticia()
        # Primeiro vai pegar todas as informaçoes que serão postadas
        for item in postar:
            titulo_noticia = (item['titulo'])
            imagem = (item['imagem'])
            texto = (item['texto'])
            link_noticia = (item['link'])
            url = (item['url'])
        # É traduzido o titulo e depois o texto da noticia
        titulo_noticia = translator.translate(titulo_noticia, dest='pt').text  
        texto_traduzido = translator.translate(texto, dest='pt').text 
        # No final da noticia original tem uns links deles, vamos pegar todo o texto antes disso
        cortando_o_texto = texto_traduzido.split("Artigos relacionados:", 1)
        # Aqui vamos deixar ele organizado para postar
        noticia = (cortando_o_texto[0]).replace("\n\n", "\n").replace("\n", "<br /><br />")
        # Essa parte é da Api do Blogger, recomendo nao mexer
        service, flags = sample_tools.init(
          argv, 'blogger', 'v3', __doc__, __file__,
          scope='https://www.googleapis.com/auth/blogger')
        try:
          users = service.users()
          thisuser = users.get(userId='self').execute()
          blogs = service.blogs()
          thisusersblogs = blogs.listByUser(userId='self').execute()
          posts = service.posts()
          blog = thisusersblogs['items'][0]
          # Aqui vai buscar a Id do blogger que esta no arquivo json 
          if blog['id'] == id_do_blogger:
              body = {
        "kind": "blogger#post",
# Titulo
        "title": "%s" % (titulo_noticia.upper()),
# Essa parte Html é todo o corpo da noticia, recomendo vc ir testando o melhor formato para seu blog 
        "content": """
<div><p>&nbsp; <span style="font-size: x-large;"></span><span style="font-size: x-large;"><a href="%s"style="margin-left: 1em; margin-right: 1em;">
<img border="0" data-original-height="684" data-original-width="684" height="385" src="%s"width="600" /></a></span></p><p></p><p>
<span style="font-size: large;">Quer apoiar meu projeto de divulgação de noticias?
<a href="https://apoia.se/samirnews" rel="nofollow" target="_blank">Agora é possivel</a><br /><br />
<span style="font-size: large;">%s</span>
<p><b><span style="font-size: large;">Veja a noticia completa em: <a href="%s">%s</a></span></b><br /></p><p>
<p><b><span style="font-size: large;">Fonte: <a href="%s">%s</a></span></b><br /></p><p>&nbsp;</p><p>
<span style="font-size: large;">Achou esse artigo interessante? Siga canalfsociety em 
<a href="https://www.instagram.com/canalfsociety" rel="nofollow" target="_blank">Instagram</a>, 
<a href="http://facebook.com/canalfsociety" rel="nofollow" target="_blank">Facebook</a>, 
<a href="https://t.me/canalfs0ciety" rel="nofollow" target="_blank">Telegram</a>, 
<a href="https://twitter.com/CanalFs0ciety" rel="nofollow" target="_blank">Twitter</a>, 
<a href="https://play.google.com/store/apps/details?id=com.canalfs0ciety.boletimtec" rel="nofollow" target="_blank">App Boletim Tec</a> e 
<a href="https://play.google.com/store/apps/details?id=com.canalfsociety.mrrobotsticker" 
rel="nofollow" target="_blank">App Mr Robot Sticker</a> para ler mais conteúdo exclusivo que postamos.</span> <br /></p></div>
""" % (imagem, imagem, noticia, link_noticia, link_noticia, url, url)}
          posts.insert(blogId=blog['id'], body=body, isDraft=False).execute()
        except client.AccessTokenRefreshError:
          print ('The credentials have been revoked or expired, please re-run'
               'the application to re-authorize')
        # Se tudo der certo, sua noticia estara postada no blogger       
        print ("NOVA NOTICIA POSTADA")

    # Agora vamos divulgar as noticias nas redes sociais, no caso vai pegar a noticia que acabou de ser postada no seu blog
    # É realizado um web scraping no seu blog para pegar o titulo, link e imagem da noticia
    def divulga_get(self):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0'}
        r = requests.get('https://www.canalfsociety.com/', headers=headers)
        content = Soup(r.text, 'html.parser')
        tittle_class = 'entry-header'
        cards = content.find_all('article', {'class': 'blog-post hentry index-post post-0'})
        canalfso = []
        for card in cards:
            canalfso.append({
                'link': card.find('div', {'class': tittle_class}).find('a').get('href'),})
        for item in canalfso:
            link = (item['link'])
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0'}
        r = requests.get(link, headers=headers)
        content = Soup(r.text, 'html.parser')
        image_class = 'post-body'
        cards = content.find_all('div', {'class': 'item-post-inner'})
        canalfsociety = []
        for card in cards:
            canalfsociety.append({
                'titulo': card.find('h1').text,
                'imagem': card.find('div', {'id': image_class}).find('a').find('img').get('src'),
                'link': link,})
        return canalfsociety

    # Aqui é realizado a divulgação
    def divulga_post(self):
        canalfsociety = self.divulga_get()  
        # Essa são as variaveis que vão ser usadas          
        for item in canalfsociety:
            titulo = (item['titulo'])
            link_noticia = (item['link'])
            imagem = (item['imagem'])    

        # Primeiro sera divulgada no Telegram
        bot_token = telegram_bot_token
        chat = chat_id
        # Aqui voce configura como sera enviada a mensagem, no caso esta para ir o titulo, pular uma linha e depois o link
        message = titulo + "\n" + link_noticia
        requests.post("https://api.telegram.org/bot" + bot_token +"/sendMessage?chat_id=" + chat +"&text=" + message)
        print ("Postado no Telegram") 
        time.sleep(1)

        # Agora sera divulgado no Twitter
        twit = tweepy.Client(consumer_key=twitter_consumer_key,
                            consumer_secret=twitter_consumer_secret,
                            access_token=twitter_access_token,
                            access_token_secret=twitter_access_token_secret)
        response = twit.create_tweet(text='#SamirNews: %s %s' % (titulo,link_noticia))
        print ("Postado no Twitter")
        time.sleep(1)

        # Aqui vai postar em sua pagina do facebook
        facetoken = token_do_facebook
        id = id_facebook
        graph = facebook.GraphAPI(facetoken)
        graph.put_object(id, "feed", message="%s" % (titulo), link="%s" % (link_noticia))
        print ("Postado no Facebook")
        time.sleep(1) 

        # Aqui é a parte do Discord
        payload = {
            'content': "%s" % titulo + "\n" + link_noticia
        }
        header = {
            'authorization': token_discord
        }
        # Pegue o Id do seu canal e coloque no local indicado
        r = requests.post("https://discord.com/api/v9/channels/ID_DO_CANAL_DISCORD/messages", data=payload, headers=header)
        print ("Postado no Discord")
        time.sleep(1) 

        # E por ultimo ser postado no feed do Instagram
        ig_user_id = id_do_instagram
        insta_token = token_instagram
        def postInstagramQuote():
            post_url = 'https://graph.facebook.com/v13.0/%s/media' % ig_user_id
            payload = {
                    'image_url': imagem,
                    # Aqui sera a legenda da sua foto, segue um exemplo do jeito que uso, nao colocar links aqui
                    'caption': (titulo + "\n" + "\n" + "Veja essa noticia completa no app BOLETIM TEC ou no link que esta na bio" +
                     "\n" + "\n" + "#hacker #news #ciberseguranca #boletimtec #tecnologia"),
                    "access_token": insta_token,
                }
            r = requests.post(post_url, params=payload)       
            result = json.loads(r.text)
            if 'id' in result:
                creation_id = result['id']    
                second_url = 'https://graph.facebook.com/v13.0/%s/media_publish' % ig_user_id
                second_payload = {
                    'creation_id': creation_id,
                    'access_token': insta_token
                    }
                r = requests.post(second_url, data=second_payload)
            else:
                print('Erro no Instagram')
        postInstagramQuote()
        print ("Postado no Instagram")
        time.sleep(1)
    # Finalizado o envio
 
DivulgaNoticias().main()
