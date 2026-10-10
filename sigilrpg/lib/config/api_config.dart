/// Configuração da URL da API
/// 
/// Para usar em dispositivo físico Android:
/// 1. Conecte seu notebook ao hotspot do celular OU conecte ambos na mesma rede Wi-Fi
/// 2. Descubra o IP do seu notebook:
///    - Windows: abra PowerShell e digite `ipconfig`, procure "IPv4" na interface Wi-Fi
///    - Exemplo: 192.168.43.100 ou 192.168.137.50
/// 3. Altere o IP abaixo para o IP do seu notebook
/// 4. Recompile o APK
/// 
/// IMPORTANTE: Este IP só funciona quando:
/// - Celular e notebook estão na mesma rede (Wi-Fi ou hotspot)
/// - A API está rodando no notebook
/// - O firewall permite conexões na porta 8000

class ApiConfig {
  /// IP do servidor (seu notebook)
  /// Altere este valor para o IP do seu notebook na rede local
  /// Exemplos:
  /// - Hotspot do celular: geralmente 192.168.43.x ou 192.168.137.x
  /// - Wi-Fi do IF: o IP que o IF atribuiu ao seu notebook
  static const String serverIp = '192.168.1.5'; // ⬅️ IP do seu notebook
  
  /// Porta da API
  static const int serverPort = 8000;
  
  /// URL completa do servidor (gerada automaticamente)
  static String get baseUrl => 'http://$serverIp:$serverPort';
}

