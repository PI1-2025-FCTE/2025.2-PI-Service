import sys
import json
import time
import random
import datetime
import paho.mqtt.client as mqtt
import threading

class ESP32Simulator:
    """
    Simula uma ESP32 com conexão MQTT, gerenciamento de bateria, LWT e
    processamento de comandos de movimentação.
    """

    def __init__(self, device_id, broker="localhost", port=1883):
        """
        Inicializa o dispositivo virtual.
        """
        self.device_id = device_id
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=device_id)
        
        self.battery = 100.0
        self.online = False
        
        self.topic_commands = f"devices/{self.device_id}/commands"
        self.topic_status = f"devices/{self.device_id}/status"
        self.topic_trajeto = f"devices/{self.device_id}/trajeto"

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def _get_timestamp(self):
        """
        Retorna o timestamp atual em formato ISO.
        """
        return datetime.datetime.now().isoformat()

    def configure_lwt(self):
        """
        Configura o Last Will and Testament (LWT) para indicar desconexão inesperada.
        """
        payload = json.dumps({
            "battery": None,
            "online": False,
            "timestamp": self._get_timestamp()
        })
        self.client.will_set(self.topic_status, payload=payload, qos=1, retain=True)

    def on_connect(self, client, userdata, flags, reason_code, properties):
        """
        Callback executado ao conectar ao broker.
        """
        if reason_code == 0:
            print(f"[{self.device_id}] Conectado ao broker MQTT.")
            self.online = True
            client.subscribe(self.topic_commands)
            print(f"[{self.device_id}] Inscrito em: {self.topic_commands}")
            self.publish_status()
        else:
            print(f"[{self.device_id}] Falha na conexão. Código: {reason_code}")

    def process_commands(self, command_str):
        """
        Analisa a string de comandos recebida, simula o tempo de execução
        e separa o ID do trajeto.
        """
        index = 0
        commands_executed = ""
        trajectory_id = None
        total_simulated_time = 0.0

        print(f"[{self.device_id}] Processando comandos: {command_str}")

        while index < len(command_str):
            char = command_str[index]
            
            if char == 'a':
                if index + 4 < len(command_str):
                    digits = command_str[index+1 : index+5]
                    commands_executed += f"a{digits}"
                    distance = int(digits)
                    # Simula: 0.05s por cm
                    total_simulated_time += (distance * 0.01)
                    index += 5
                else:
                    break
            
            elif char == 'e':
                commands_executed += "e"
                total_simulated_time += 1.0
                index += 1
            
            elif char == 'd':
                commands_executed += "d"
                total_simulated_time += 1.0
                index += 1
            
            elif char == 'i':
                trajectory_id = command_str[index+1:]
                break
                
            else:
                index += 1

        return commands_executed, trajectory_id, total_simulated_time

    def on_message(self, client, userdata, msg):
        """
        Callback executado ao receber uma mensagem no tópico inscrito.
        """
        payload_str = msg.payload.decode('utf-8')
        print(f"[{self.device_id}] Comando recebido: {payload_str}")

        cmds_exec, traj_id, sim_time = self.process_commands(payload_str)

        if traj_id:
            threading.Thread(
                target=self.execute_trajectory, 
                args=(cmds_exec, traj_id, sim_time),
                daemon=True
            ).start()
    
    def execute_trajectory(self, cmds_exec, traj_id, sim_time):
        """
        Executa o trajeto simulando o tempo de execução.
        """
        print(f"[{self.device_id}] Executando trajeto... (Aguardando {sim_time:.2f}s)")
        time.sleep(sim_time)

        self.battery = max(0, self.battery - (sim_time * 0.5))

        result_payload = json.dumps({
            "comandosExecutados": cmds_exec,
            "idTrajeto": traj_id,
            "tempo": int(sim_time)
        })
        
        self.client.publish(self.topic_trajeto, result_payload, qos=1)
        print(f"[{self.device_id}] Trajeto finalizado. Publicado em {self.topic_trajeto}")
        
        self.publish_status()

    def publish_status(self):
        """
        Publica o estado atual da bateria e conectividade.
        """
        payload = json.dumps({
            "battery": round(self.battery, 2),
            "online": self.online,
            "timestamp": self._get_timestamp()
        })
        self.client.publish(self.topic_status, payload, retain=True)

    def run(self):
        """
        Inicia o loop principal do dispositivo.
        """
        self.configure_lwt()
        
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()

            while True:
                time.sleep(5) 
                
                if self.battery > 0:
                    decay = random.uniform(0.1, 0.5)
                    self.battery = max(0, self.battery - decay)
                else:
                    self.battery = 0
                
                self.publish_status()

        except KeyboardInterrupt:
            print(f"\n[{self.device_id}] Desligando...")
            off_payload = json.dumps({"battery": None, "online": False, "timestamp": self._get_timestamp()})
            self.client.publish(self.topic_status, off_payload, qos=1,retain=True)
            self.client.disconnect()
            self.client.loop_stop()
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        my_id = sys.argv[1]
    else:
        my_id = "esp32_default"

    device = ESP32Simulator(device_id=my_id)
    device.run()