from __future__ import division
import falcon, os, sys, magic, requests, json, time, math, decimal
#from falcon_cors import CORS

#cors_allow_all = CORS(allow_all_origins=True, allow_all_headers=True, allow_all_methods=True,allow_credentials_all_origins=True)
#cors = cors_allow_all
#api = falcon.API(middleware=[cors.middleware])

from falcon.http_status import HTTPStatus

def numToWords( i = 0 ):
    limit = 999999999999 # // make this 999999999999999 to support trillioni
    if i > limit or i < 0:
        return 'Out of Range!!!'
    if i == 0:
        return 'zero'
    init = 1000000000 # // make this 1000000000000 to support trillion
    st = 0
    start = [ 'billion', 'million', 'thousand', '' ] # // make this [ 'trillion', 'billion', 'million', 'thousand' ] to support trillion
    words = [ '', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen','fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty' ]
    tens = ['','','twenty','thirty', 'fourty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
    fin = []
    while i > 0:
        dv = math.floor(i / init)
        if dv > 0:
            h = 100
            xdv = dv
            if math.floor(xdv/h) > 0:
                fin.append( words[math.floor(xdv/h)] + ' hundred' )
                i -= math.floor(xdv/h) * h * init
                xdv = xdv % h
            if xdv <= 20 and xdv > 0:
                fin.append(words[int(xdv)])
                if st < len(start):
                    fin.append(start[st])
                i -= init * xdv
            else:
                t = 10
                if math.floor(xdv / t) > 0:
                    fin.append( tens[math.floor(xdv/t)])
                    i -= math.floor(xdv/t) * t * init
                    xdv = xdv % t
                if xdv > 0:
                    fin.append( words[int(xdv)] )
                    i -= (xdv) * init
                if st < len(start):
                    fin.append(start[st])
        st += 1
        init /= 1000
    return (' '.join(fin)).strip()

class HandleCORS(object):
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', '*')
        resp.set_header('Access-Control-Allow-Headers', '*')
        resp.set_header('Access-Control-Max-Age', 1728000)  # 20 days
        if req.method == 'OPTIONS':
            raise HTTPStatus(falcon.HTTP_200, body='\n')

class InventoryResource:
    #cors = cors_allow_all
    def on_get(self, request, response):
        response.status = falcon.HTTP_200
        prm = request.params

        pids = prm.get('pids','-')
        pidsXt = pids.split(',')
        pids = ','.join(list(set(pidsXt)))

        #urlx = 'https://www.'+prm.get('site','-').lower()+'.com/s/'+prm.get('site','-')+'/dw/shop/v18_3/products/(' + pids + ')?client_id=58b918ff-a2ae-4a37-bd3a-cdcce8ebd790&expand=availability,images,prices'
        urlx = 'https://dev05-web-jnj.demandware.net/s/'+prm.get('site','-')+'/dw/shop/v18_3/products/(' + pids + ')?client_id=58b918ff-a2ae-4a37-bd3a-cdcce8ebd790&expand=availability,images,prices'
        print('urlx : ' , urlx)

        if prm.get('getfile', '-') != '-':
            urlx = 'http://web.lalaseng.com/Trainings/AJ/gallery-data.json'

        r = requests.get(urlx)
        response.content_type = 'application/json'
        #print('r.json() :', r.json())
        response.body = r.text #json.dumps(r.json())

class NumToWordsResource:
    def on_get(self, request, response):
        response.status = falcon.HTTP_200
        prm = request.params
        num = int(prm.get('number', -1))
        response.content_type = 'application/json'
        response.body = json.dumps({'number':num, 'words':numToWords(num)})

class DataResource:
    #cors = cors_allow_all
    def on_get(self, request, response):
        import datetime, hashlib
        import mysql.connector
        response.status = falcon.HTTP_200
        prm = request.params

        ses_key = request.get_cookie_values('youfoo')
        print('getCookie Value: %s' % ses_key)
        if ses_key:
            # do Nothing
            print('ses_key: %s' % ses_key)
        else:
            ses_key = '%s - %s' % ( str(time.time()), hashlib.md5( str(time.time()).encode() ).hexdigest()[-10:])
            response.set_cookie('youfoo', ses_key)

        config = {
          'user': 'root',
          'password': 'larryvel',
          'host': 'web.lalaseng.com',
          'database': 'pcga',
          'raise_on_warnings': True
        }

        cnx = mysql.connector.connect(**config)
        #cursor = cnx.cursor()
        cursor = cnx.cursor(dictionary=True)

        query = ("SELECT * from offices")
        if prm.get('q', '-') != '-':
            query = (prm['q'])

        cursor.execute(query)

        data = []
        if cursor.rowcount:
            for c in cursor:
                data.append(c)

        response.content_type = 'application/json'
        if prm.get('debug', '-') == '1':
            response.content_type = 'text/html'
            response.body = '<pre>%s</pre>' % json.dumps({'ses': ses_key, 'data': data}, cls=DecimalEncoder, indent=4) 
        else:
            response.body = json.dumps({'ses': ses_key, 'data': data}, cls=DecimalEncoder)

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


class HelloWorldResource:

    def on_get(self, request, response):
        response.status = falcon.HTTP_200
        response.content_type = 'text/html'
        response.body = '<html><head><title>Proj El MaSa</title><link rel="preconnect" href="https://fonts.gstatic.com"><link href="https://fonts.googleapis.com/css2?family=Anton&family=Sigmar+One&display=swap" rel="stylesheet"></head><style>img{width: 150px; margin: 10px;} body {font-family: \'Anton\', sans-serif; font-size: 30px; background-color: #eee;}</style><body style="margin:50px auto; text-align: center;">Oh Yeah Oh yeah!!!...<br><img src="https://miro.medium.com/max/2404/1*JUOITpaBdlrMP9D__-K5Fw.png"/><img src="https://www.nicepng.com/png/full/336-3363223_mariadb-logo-png.png"/><img src="https://res.cloudinary.com/practicaldev/image/fetch/s--2VEicJ4s--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_880/https://thepracticaldev.s3.amazonaws.com/i/yki4uug1o4nlkwfmieph.png"/><img src="https://i1.wp.com/thequickblog.com/wp-content/uploads/2020/05/laravel.png"/><br/>running in an Alpine Linux container.<br/><br/><img src="/static/beastArds.jpg" style="width: 80%"/></body></html>' 

class StaticResource(object):
    def on_get(self, req, resp, filename):
        # do some sanity check on the filename
        fpath = '/app/static/' + filename
        if os.path.isfile(fpath) == False:
            handle_404(req, resp) 
        else:
            resp.status = falcon.HTTP_200
            resp.content_type = magic.from_file(fpath, mime=True)
            #resp.stream, resp.stream_len = open(fpath)
            with open(fpath, 'rb') as f:
                resp.body = f.read()
        #resp.content_type = 'appropriate/content-type'
        #with open('/app/'+filename, 'r') as f:
        #    resp.body = f.read()

def handle_404(req, resp):
    resp.status = falcon.HTTP_404
    resp.content_type = 'text/html'
    resp.body = "<style>*{    transition: all 0.6s;}html {    height: 100%;}body{    font-family: 'Lato', sans-serif;    color: #888;    margin: 0;}#main{    display: table;    width: 100%;    height: 100vh;    text-align: center;}.fof{      display: table-cell;      vertical-align: middle;}.fof h1{      font-size: 50px;      display: inline-block;      padding-right: 12px;      animation: type .5s alternate infinite;}@keyframes type{      from{box-shadow: inset -3px 0px 0px #888;}      to{box-shadow: inset -3px 0px 0px transparent;}}</style><div id='main'><div class='fof'><h1>Error 404</h1></div></div>"

#app = falcon.API()

#app = api = Flask(__name__)

app = api = falcon.API(middleware=[HandleCORS() ])

# Enable a simple CORS policy for all responses
#app = falcon.App(cors_enable=False)

# Enable CORS policy for example.com and allows credentials
#app = falcon.App(middleware=falcon.CORSMiddleware(
#        allow_origins='172.104.160.100', allow_credentials='*'))

app.add_route('/', HelloWorldResource())
app.add_route('/inventory', InventoryResource())
app.add_route('/numtowords', NumToWordsResource())
app.add_route('/mysqldata', DataResource())
app.add_route('/static/{filename}', StaticResource())
app.add_sink(handle_404, '')
