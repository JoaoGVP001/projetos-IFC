# 📱 Como Configurar o IP da API para Funcionar no APK

## 🎯 Situação

Quando você gera um APK e instala no celular físico, o app precisa saber qual é o IP do seu notebook onde a API está rodando.

## ✅ Funciona com Hotspot do Celular?

**SIM!** Funciona perfeitamente quando você:
1. Liga o hotspot do celular
2. Conecta o notebook ao hotspot do celular
3. Descobre o IP do notebook na rede do hotspot
4. Configura esse IP no app

## 📋 Passo a Passo

### 1️⃣ Ligar o Hotspot do Celular

- Android: Configurações → Hotspot e Tethering → Hotspot Wi‑Fi
- iPhone: Configurações → Hotspot Pessoal

### 2️⃣ Conectar o Notebook ao Hotspot

- No notebook, procure a rede Wi‑Fi do celular e conecte
- Digite a senha do hotspot

### 3️⃣ Descobrir o IP do Notebook

**Windows:**
```powershell
# Abra PowerShell e digite:
ipconfig

# Procure por "Adaptador de Rede sem Fio Wi-Fi" ou similar
# Procure a linha "IPv4" - esse é o IP que você precisa!
# Exemplo: 192.168.43.100 ou 192.168.137.50
```

**Linux/Mac:**
```bash
ifconfig
# ou
ip addr
```

### 4️⃣ Configurar o IP no App

1. Abra o arquivo: `lib/config/api_config.dart`
2. Encontre a linha:
   ```dart
   static const String serverIp = '192.168.43.100'; // ⬅️ ALTERE AQUI!
   ```
3. Altere para o IP do seu notebook (o que você descobriu no passo 3)
4. Salve o arquivo

### 5️⃣ Recompilar o APK

```bash
flutter build apk --release
```

O APK estará em: `build/app/outputs/flutter-apk/app-release.apk`

### 6️⃣ Testar

1. Instale o APK no celular
2. Certifique-se de que:
   - O hotspot do celular está ligado
   - O notebook está conectado ao hotspot
   - A API está rodando no notebook (`python app.py` na pasta `SigilRPG_API-main`)
3. Abra o app no celular e teste!

## 🔥 Dicas Importantes

### ⚠️ Firewall do Windows

Se não funcionar, pode ser o firewall bloqueando. Para permitir:

1. Abra "Firewall do Windows Defender"
2. Clique em "Configurações Avançadas"
3. Clique em "Regras de Entrada" → "Nova Regra"
4. Escolha "Porta" → Próximo
5. Escolha "TCP" e digite "8000" → Próximo
6. Escolha "Permitir a conexão" → Próximo
7. Marque todas as opções → Próximo
8. Dê um nome (ex: "API Flask") → Concluir

### 🔄 IP Muda?

Se o IP do notebook mudar (acontece quando você reconecta ao hotspot), você precisa:
1. Descobrir o novo IP (`ipconfig`)
2. Atualizar `lib/config/api_config.dart`
3. Recompilar o APK

### 🏫 No IF (Instituto Federal)

Se você estiver no IF e ambos (celular e notebook) estiverem na mesma rede Wi‑Fi do IF:
- Funciona da mesma forma!
- Só precisa descobrir o IP do notebook na rede do IF
- Configurar no `api_config.dart`
- Recompilar o APK

## 🎮 Modo Emulador vs Dispositivo Físico

O código detecta automaticamente:
- **Emulador Android**: usa `10.0.2.2:8000` (IP especial do emulador)
- **Dispositivo Físico**: usa o IP configurado em `api_config.dart`

Se você quiser forçar o uso do emulador, edite `lib/utils/api.dart` e descomente a linha do emulador.

## ❓ Problemas Comuns

### "Não consegue conectar"
- ✅ Verifique se a API está rodando (`python app.py`)
- ✅ Verifique se o IP está correto
- ✅ Verifique se notebook e celular estão na mesma rede
- ✅ Verifique o firewall

### "IP mudou"
- Descubra o novo IP e atualize `api_config.dart`
- Recompile o APK

### "Funciona no emulador mas não no celular"
- Isso é normal! Emulador usa `10.0.2.2`, celular físico precisa do IP real
- Configure o IP em `api_config.dart` e recompile

