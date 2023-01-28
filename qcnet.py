#!/home/apps/python3.venv/bin/python3

import time
import logging
import mysql.connector
from configobj import ConfigObj
from datetime import datetime
from ping3 import ping
from statistics import mean

def saveData(mysqlConfig, queryReport):
	logging.info("[QCNET][INFO] Saving data")
	try:
		db = mysql.connector.connect(**mysqlConfig)
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			logging.info("[QCNET][ERROR] Something is wrong with your MySQL username or password")
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			logging.info("[QCNET][ERROR] MySQL Database not exist")
		else:
			resultAPI = err
	else:
		cursor = db.cursor()
		for query in queryReport:
			#print(query)
			cursor.execute(query)
			db.commit()
		db.close()

if __name__ == "__main__":
	configFile = "/etc/qcnet/qcnet.ini"
	conf = ConfigObj(configFile)

	logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt=conf['log']['timeformat'], filename=conf['log']['file'] )
	logging.info("[QCNET] ============== STARTING PROGRAM ==============")
	logging.info("[QCNET] read Quality Control NETwork configuration at %s", configFile)

	mysqlConfig = { 'user':conf['mysql']['username'], 'password':conf['mysql']['password'], 'host':conf['mysql']['host'], 'database':conf['mysql']['database'], 'raise_on_warnings': True}
	queryIP = "SELECT * FROM `cctv_ip`;"
	tempREPORT = "INSERT INTO `cctv_status` (`id`,`cctv_ip_ip_address`,`check`,`live`,`reply`,`min`,`ave`,`max`) VALUES (NULL,'{cctv_ip_ip_address}',{check},{live},{reply},{minimal},{average},{maximal});"


	try:
		db = mysql.connector.connect(**mysqlConfig)
	except mysql.connector.Error as err:
		if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
			logging.info("[%s][ERROR] Something is wrong with your MySQL username or password", cctv['name'])
		elif err.errno == errorcode.ER_BAD_DB_ERROR:
			logging.info("[%s][ERROR] MySQL Database not exist", cctv['name'])
		else:
			resultAPI = err
	else:
		cursor = db.cursor(dictionary=True)
		cursor.execute(queryIP)
		rows = cursor.fetchall()
		db.close()

		while True:
			queryREPORT = []
			for row in rows:
				temp = []
				success = 0
				new = True
				now = datetime.now().strftime("%Y%m%d%H%M%S")
				for i in range(int(conf['ping']['count'])):
					result = ping(row['ip_address'], unit=conf['ping']['unit'])
					if result:
						success += 1
						new = False
						temp.append(result)
					elif new and i >= int(conf['ping']['rtoconsec']):
							temp.append(0)
							break
				logging.info("[QCNET] checking IP Address: %s", row['ip_address'])
				#print(now, " -> ", row['ip_address'])
				if success > 0:
					queryREPORT.append(tempREPORT.format(cctv_ip_ip_address = row['ip_address'],
														 check = now,
														 live = True,
														 reply = int(100 * success/(int(conf['ping']['count']))),
														 minimal = round(min(temp),3),
														 average = round(mean(temp),3),
														 maximal = round(max(temp),3)))
				else:
					queryREPORT.append(tempREPORT.format(cctv_ip_ip_address = row['ip_address'],
														 check = now,
														 live = False,
														 reply = 0,
														 minimal = 0,
														 average = 0,
														 maximal = 0))

				
				#print("success: ", int(100 * success/(int(conf['ping']['count']))))
				#print(min(temp), mean(temp), max(temp))
			saveData(mysqlConfig, queryREPORT)
			logging.info("[QCNET] sleeping..... zzzzzzzz")
			time.sleep(int(conf['ping']['check_every']))
			logging.info("[QCNET] wake up!!!!")

	logging.info("[QCNET] ============== PROGRAM STOPPED ==============")