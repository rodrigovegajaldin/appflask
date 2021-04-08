from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import threading
import time
import os
import json
import paho.mqtt.client as mqtt
import ssl




class history(threading.Thread):
	def __init__(self,cliente,info,socket):
		threading.Thread.__init__(self)
		#global detener
		#self.detener = detener
		#print('este es de ',self.detener[1])
		self.bool=False
		self.cliente = cliente
		self.finaldata = []
		#self.detener = detener
		self.socket = socket
		self.info = info
		self.ddb = boto3.resource('dynamodb')#,endpoint_url='http://localhost:8001')
		self.table = self.ddb.Table('breath_ddb')
		print('los tipos de datos son: ', type(self.info[1]),self.info[1])
	def run(self):
		global detener
		print('epece el query')
		self.response = self.table.query(
			KeyConditionExpression='#pt = :usser AND #mt BETWEEN :start_time AND :end_time',
			ExpressionAttributeNames={
				"#pt" : "id",
				"#mt": "timestamp"
			},
			ExpressionAttributeValues={
				':usser' : self.info[0],
				':start_time':Decimal(self.info[1]),
				':end_time':Decimal(self.info[2])
			}
		)
		page = True
		while page and not detener[self.cliente]:
		
			self.data = self.response['Items']
			if self.bool:
				self.finaldata += self.data
			"""for item in self.data:
				#print('item es: ',item)
				#emit(self.sensor,json.loads(str(item).replace('Decimal(','').replace(')','').replace("'",'"')),room=self.cliente)
				data = json.loads(str(item).replace('Decimal(','').replace(')','').replace("'",'"'))
				self.socket.emit('data',data,room=self.cliente)
				time.sleep(0.1)
				if detener[self.cliente]:
					print('se detuvo el envio: ',detener[self.cliente])
					break"""
			
			#emit('o',json.loads(item),room=self.cliente)
			if 'LastEvaluatedKey' in self.response.keys():
				self.paginating(self.response['LastEvaluatedKey'])
			else:
				page = False 
			print('termine una vuelta',len(self.data))

		print('el tamano de los resultados es: ')#,len(self.data))

	def paginating(self,lastkey):
		self.response = self.table.query(
			KeyConditionExpression='#pt = :usser AND #mt BETWEEN :start_time AND :end_time',
			ExpressionAttributeNames={
				"#pt" : "id",
				"#mt": "timestamp"
			},
			ExpressionAttributeValues={
				':usser' : self.info[0],
				':start_time':Decimal(self.info[1]),
				':end_time':Decimal(self.info[2])
			},
			ExclusiveStartKey=lastkey
		)
	def notthread(self):
		self.run()
		return self.finaldata
"""class fixer(threading.Thread):
	def __init__(self,patient,socket):
		threading.Thread.__init__(self)
		#self.list = lista.copy()
		#self.stream = stream
		#self.sensor = sensor
		self.socket = socket
		self.patient = patient
		self.ddb = boto3.resource('dynamodb',endpoint_url='http://localhost:5001')

	def run(self):
		time.sleep(5)
		global detener#free, final, solicitud, rtpatients
		lastvalue = {'o':0,'a':0,'f':0}
		data = [0,0,0]
		data[0] = self.query(self.patient,'o',lastvalue['o'])
		data[1] = self.query(self.patient,'a',lastvalue['a'])
		data[2] = self.query(self.patient,'f',lastvalue['f'])

		if len(data[0]) != 0:
			lastvalue['o']=data[0][0]['serie']+1
		if len(data[1]) != 0:
			lastvalue['a']=data[1][0]['serie']+1
		if len(data[2]) != 0:
			lastvalue['f']=data[2][0]['serie']+1
		#init = self.ddb.Table(self.patient).scan()
		#init=init['Items'][0]
		print('la data es:\n',lastvalue)
		#print('inicie con :',init['sensor'])
		#rest = {}
		while not detener[self.patient]:
			#free = False
			#print('soy el thread de:',self.sensor)
			#print('soy el thrad ordenador',threading.current_thread())
			#print('rest:',len(rest),'original:',len(self.list))
			data[0] = self.query(self.patient,'o',lastvalue['o'])
			data[1] = self.query(self.patient,'a',lastvalue['a'])
			data[2] = self.query(self.patient,'f',lastvalue['f'])
			#data = self.scan(self.patient,{'sensor':init['sensor'],'serie':init['serie']})
			#print('nuevo',data[1][0],data[0][0],data[2][0])
			#print('tamano de oximetro: ',len(data[0]))
			#print('despues:',len(self.list))
			#ordenado = sorted(self.list)
			#print('ordenado es: ', ordenado)
			#print('antes de enviar',len(self.list))

			for item in data:
				if item['serie'] == lastvalue[item['sensor']]:
					self.socket.emit('data',json.loads(item['data'].replace('Decimal(','').replace(')','').replace("'",'"')),room=self.patient)
					lastvalue[item['sensor']] += 1
					#print('envie valor')
				else:
					init = item 
					init['serie']= lastvalue[item['sensor']]-1
					break


			for sensordata in data:
				for item in sensordata:
					if item['serie'] == lastvalue[item['sensor']]:
						self.socket.emit('data',json.loads(item['data'].replace('Decimal(','').replace(')','').replace("'",'"')),room=self.patient)#broadcast=True)
						lastvalue[item['sensor']] += 1
					else:
						break
			#print('termine de enviar')
	def query(self,patient,sensor,start):

		response = self.ddb.Table(patient).query(
			KeyConditionExpression= '#sensor = :sensor and #start >= :start',
			ExpressionAttributeNames={
				"#sensor" : 'sensor',
				"#start" : 'serie'
			},
			ExpressionAttributeValues={
				':sensor' : sensor,
				':start' : start
			}
		)
		return response['Items']

	def scan(self,patient,startkey):
		response = self.ddb.Table(patient).scan(
			ExclusiveStartKey = startkey
			)
		return response['Items']"""

class fixer(threading.Thread):
	def __init__(self,patient,socket):
		threading.Thread.__init__(self)
		#self.list = lista.copy()
		#self.stream = stream
		#self.sensor = sensor
		self.socket = socket
		self.patient = patient
		self.ddb = boto3.resource('dynamodb')#,endpoint_url='http://localhost:5001')
		self.table = self.ddb.Table('breath_ddb')
		print('inicie a leer')

	def run(self):
		#time.sleep(5)
		print('inicie a leer')
		global detener#free, final, solicitud, rtpatients
		now = time.time()*1000000
		#lastvalue = {'o':0,'a':0,'f':0}
		#data = [0,0,0]
		#data[0] = self.query(self.patient,,Decimal(now))
		#data[1] = self.query(self.patient,,Decimal(now))
		#data[2] = self.query(self.patient,,Decimal(now))
		lastvalue =Decimal(0)
		data=self.query(int(self.patient),Decimal(now))
		if len(data)!= 0:
			lastvalue = data[-1]['timestamp']

		#if len(data[0]) != 0:
		#	lastvalue['o']=data[0][-1]['timestamp']
		#if len(data[1]) != 0:
		#	lastvalue['a']=data[1][-1]['timestamp']
		#if len(data[2]) != 0:
		#	lastvalue['f']=data[2][-1]['timestamp']
		#init = self.ddb.Table(self.patient).scan()
		#init=init['Items'][0]
		print('la data es:\n',lastvalue)
		#print('inicie con :',init['sensor'])
		#rest = {}
		while not detener[self.patient]:
			#free = False
			#print('soy el thread de:',self.sensor)
			#print('soy el thrad ordenador',threading.current_thread())
			#print('rest:',len(rest),'original:',len(self.list))
			

			#data[0] = self.query(self.patient,'o',lastvalue['o'])
			#data[1] = self.query(self.patient,'a',lastvalue['a'])
			#data[2] = self.query(self.patient,'f',lastvalue['f'])
			
			data = self.query(int(self.patient),lastvalue)
			lastvalue = data[-1]['timestamp']
			#data = self.scan(self.patient,{'sensor':init['sensor'],'serie':init['serie']})
			#print('nuevo',data[1][0],data[0][0],data[2][0])
			#print('tamano de oximetro: ',len(data[0]))
			#print('despues:',len(self.list))
			#ordenado = sorted(self.list)
			#print('ordenado es: ', ordenado)
			#print('antes de enviar',len(self.list))

			"""for item in data:
				if item['serie'] == lastvalue[item['sensor']]:
					self.socket.emit('data',json.loads(item['data'].replace('Decimal(','').replace(')','').replace("'",'"')),room=self.patient)
					lastvalue[item['sensor']] += 1
					#print('envie valor')
				else:
					init = item 
					init['serie']= lastvalue[item['sensor']]-1
					break"""

			for item in data:
				self.socket.emit('data',json.loads(str(item).replace('Decimal(','').replace(')','').replace("'",'"')),room='patient'+self.patient)#broadcast=True)
			#for sensordata in data:
			#	for item in sensordata:
					#if item['serie'] == lastvalue[item['sensor']]:
			#		self.socket.emit('data',json.loads(item.replace('Decimal(','').replace(')','').replace("'",'"')),room=self.patient)#broadcast=True)
			#		print('envie valor')
						#lastvalue[item['sensor']] += 1
					#else:
					#	break
			#print('termine de enviar')
	def query(self,patient,start):


		response = self.table.query(
			KeyConditionExpression= '#id = :patient',# and #start >= :start',
			ExpressionAttributeNames={
				"#id" : 'id',
				#"#start" : 'timestamp'
			},
			ExpressionAttributeValues={
				':patient' : patient,
				#':start' : start
			},
			ExclusiveStartKey = {'id':patient,'timestamp':start}
		)
		return response['Items']

	def scan(self,patient,startkey):
		response = self.ddb.Table(patient).scan(
			ExclusiveStartKey = startkey
			)
		return response['Items']


class batch_writer(threading.Thread):
	def __init__(self,tablename,datalist):
		threading.Thread.__init__(self)
		self.datalist = datalist.copy()
		self.ddb = boto3.resource('dynamodb',endpoint_url='http://localhost:5001')
		self.tablename = tablename
		

	def run(self):
		global free
		print('inicie el batch')
		response = self.ddb.batch_write_item(RequestItems={
			self.tablename:self.datalist})
		print('respuesta del batch', response)
		free = True



class MQTTclass(threading.Thread):
	def __init__(self,socket):#,streams):
		threading.Thread.__init__(self)
		print('cree el cliente mqtt')
		global clientg, free, rest, final
		free = True#{'acelerometro':True,'flexometro':True,'oximetro':True}
		rest = {'a':{},'f':{},'o':{}}
		final = {'a':[],'f':[],'o':[]}
		
		#self.streams= streams
		self.socket = socket
		self.list = {'a':{},'f':{},'o':{}}
		self.client = mqtt.Client(client_id='mqtt'+str(os.getpid()),clean_session=False)
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.client.on_disconnect = self.on_disconnect
		self.awshost = 'alkwr3zeuqahg-ats.iot.us-west-1.amazonaws.com'
		self.awsport = 8883
		self.certpath = 'certificados/c898ffe59d-certificate.pem.crt'
		self.capath = 'certificados/amazon_root_ca.pem'
		self.keypath = 'certificados/c898ffe59d-private.pem.key'

		self.client.tls_set(self.capath,certfile=self.certpath,keyfile=self.keypath,cert_reqs=ssl.CERT_REQUIRED,tls_version=ssl.PROTOCOL_TLSv1_2,ciphers=None)

		self.client.connect(self.awshost,self.awsport,keepalive=60)
		self.client.loop_forever()
		#self.client.loop_forever()
		clientg = self.client
		#self.tos = cough_detect(self.streams,self.socket)
		#self.tos.start()
		#print('n thread', threading.enumerate())

	def on_connect(self,client,userdata,flags,rc):
		#print('---------------------------------------------------')
		#print('connect thread: ',threading.current_thread())#os.getpid())
		print('connected',client._client_id)
		#client.subscribe(topic='patient/#',qos=1)
		#print('MQTT fue atendido por el proceso: ',os.getpid())

	def on_message(self,client,userdata,msg):
		global free, rtpatients
		free=False
		msgdecode = json.loads(msg.payload.decode('utf-8'))
		topic = msg.topic.replace('/','')
		#free[topic] = False
		sensor = msgdecode['sensor']
		#rtpatients[topic][msgdecode['sensor']] = msgdecode
		#free[topic] = True
		rtpatients[topic][sensor][msgdecode['measure_n']]=msgdecode
		#print('los datos ',rtpatients[topic].keys())
		print('recivi los datos ',len(rtpatients[topic]['o']),len(rtpatients[topic]['a']),len(rtpatients[topic]['f']))
		#if len(rtpatients[topic])>10 and free:
		free = True
		#	batchthread = batch_writer(topic,rtpatients[topic])
		#	batchthread.start()
		#	rtpatients[topic].clear()
		
		"""ddb.Table(topic).put_item(
			Item = {
				'sensor' : msgdecode['sensor'],
				'serie' : int(msgdecode['measure_n']),
				'data' :  str(msgdecode)
			}   
		)"""
		
		#print('guarde valor',msgdecode['measure_n'])
		#topic = msg.topic.split('/')[1]
		#print('------------------------------------------')
		#print('topic: ',topic)
		#print('numero',msgdecode['numero'])
		#print('payload:',msgdecode)
		#self.list[sensor][msgdecode['measure_n']]=msgdecode 
		#print('oximetro:',len(self.list['oximetro']))
		#print('flexometro:',len(self.list['flexometro']))
		#print('acelerometro:',len(self.list['acelerometro']))
		
		#if len(self.list[sensor])>=10 and free:#[topic]:
			#print('las llaves1',free)
		#	free=False
			#print('las llaves2',free)
			#print('CREE EL THREAD:',topic)
			#print('mi lista:',len(self.list[topic]))
			#fixerthread = fixer(self.list[sensor],sensor,self.socket)
			#fixerthread.start()
			#print('hay tantos thrads:',len(self.ordenadorthread))
			#ordenador(self.list[topic],self.socket,self.streams[topic],topic).start()
		#	self.list[sensor].clear()

		#print(len(self.list))
		#self.socket.emit('mqtt',str(msgdecode),broadcast=True)

	def on_disconnect(self,client,userdata,flags,rc):
		print('DISCONNECTED')




global detener, rtpatients,threads, free
ddb = boto3.resource('dynamodb',endpoint_url='http://localhost:5001')
free = True
detener = {}
rtpatients = {}
threads =[]
print('thread principal: ',threading.current_thread())#os.getpid())	
print('proceso ejecutado',os.getpid())
app = Flask(__name__)
app.config['SECRET KEY'] = 'secret'
app.debug = False
socketio = SocketIO(app)
print('esta es la aplicacion')
#mqttthread = MQTTclass(socketio)


def check_tables(tablename):
	client = boto3.client('dynamodb',endpoint_url='http://localhost:5001'	)
	response = client.list_tables(
		#ExclusiveStartTableName='string',
		Limit=50
	)
	return tablename in response['TableNames']


def create_table(tablename):
	
	#def __init__(self,tablename):
	print('nombre de la tabla es: ',tablename)
	table = ddb.create_table(
		TableName = tablename,
		KeySchema = [
			{
				'AttributeName' : 'sensor',
				'KeyType' : 'HASH'	
			},
			{
				'AttributeName' : 'serie',
				'KeyType' : 'RANGE'
			}
		],
		AttributeDefinitions = [
			{
				'AttributeName' : 'sensor',
				'AttributeType' : 'S'
			},
			{
				'AttributeName' : 'serie',
				'AttributeType' : 'N'
			}
		],
		ProvisionedThroughput = {
			'ReadCapacityUnits' : 1000,
			'WriteCapacityUnits' : 1000
		}
	)
	
	table.meta.client.get_waiter('table_exists').wait(TableName=tablename)
	print('cree la tabla')

@app.route('/query')
def query():
	req = request.get_json()
	print('detecte history: ',msg)
	detener[request.sid]= False
	History = history(request.sid,msg[1:],socketio)
	History.start()

@app.route('/page2')
def page2():
	print('atendi a la pagina')
	return render_template('page_ing3.html')

@app.route('/main')
def home():
	global clientg
	#clientg.subscribe(topic='patient/3',qos=1)
	#print('---------------------------------------------------')
	#print('connect thread: ',threading.current_thread())#os.getpid())
	#print('MQTT fue atendido por el proceso: ',os.getpid())
	#print('los headers son:',request.headers)
	#print('la ip es: ',request.headers['X-Forwarded-For'])
	#return render_template('page_ing2.html')
	#mqttthread = MQTTclass()
	return render_template('index.html')

@socketio.on('connect')
def connected():

	#emit('msg', 'tu ip es: '+request.headers['X-Forwarded-For'])
	print('se conecto.....')
	print('fue atendido por el proceso: ',os.getpid())
	#contar +=[request.sid] 
	#print('hay ', contar,' conectados')
	print('la ip es: ',request.headers['X-Forwarded-For'],'\ny su id es: ',request.sid)
	#emit('msg','tu id es: '+request.sid)
	#print('mande el mensaje')
	emit('saludo','te atendio {}'.format(os.getpid()))


@socketio.on('disconnect')
def disconnect():
	print('se desconecto...')
	#contar -= 1
	#print('hay ', contar,' conectados')
	print('la ip es: ',request.headers['X-Forwarded-For'],'\ny su id es: ',request.sid)

@socketio.on('request')
def recivir(msg):
	global detener, clientg, rtpatients,threadss
	
	print('el mensaje de solicitud es: ',msg)
	if msg[0] == 'realtime':
		#patient = 'patient'+str(msg[1])
		patient = str(msg[1])
		topic = 'patient'+str(msg[1])
		detener[patient] = False
		rtpatients[patient]={'o':{},'a':{},'f':{}}
		#clientg.subscribe(topic=topic,qos=1)
		socketio.server.enter_room(request.sid,topic)
		#if not check_tables(patient):
			#rtpatients[patient] = {}
			#create_table(patient)
			#detener[patient] = False

		if topic not in str(threading.enumerate()):
			threads.append(fixer(patient,socketio))
			threads[-1].name = topic
			threads[-1].start()
		print('cree el thread del paciente')

		print('detecte realtime: ',msg)
		
	elif msg[0]=='history':
		#socketio.emit('saludo','hola',room=request.sid)
		print('detecte history: ',msg)
		detener[request.sid]= False
		History = history(request.sid,msg[1:],socketio)
		History.start()
		#print('tipo: ',type(msg))
		#print('fecha',msg[3],'timestamp',time.ctime(msg[3]))
	elif msg[0]=='stop':
		print('detecte stop: ',msg)
		print('tipo: ',type(msg))
		#socketio.rooms['']['foobar-room']

@socketio.on('saludo')
def recivir(msg):
	global detener
	detener[request.sid] = True
	print('el mensaje de saludo es: ',msg)
	#History = history(request.sid,'f',detener)
	#History.run()

"""if __name__ == '__main__':
	try:
		#App = app()
		#App.app.run(host='0.0.0.0',port=5005)
		socketio.run(app)
	except Exception as e:
				print(e)
"""