const https = require('https');

const data = JSON.stringify({
  email: 'teste@email.com',
  senha: '123456'  // ← Corrigido! Antes era "password"
});

const options = {
  hostname: 'login-backend.znh7ry.easypanel.host',
  port: 443,
  path: '/api/auth/login',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': data.length
  }
};

console.log('🔐 Testando login com payload CORRETO...\n');
console.log('📤 Enviando:', data);
console.log('');

const req = https.request(options, (res) => {
  console.log(`📊 Status: ${res.statusCode}`);
  
  let body = '';
  res.on('data', (chunk) => body += chunk);
  res.on('end', () => {
    try {
      const json = JSON.parse(body);
      
      console.log('\n✅ Response:');
      console.log(JSON.stringify(json, null, 2));
      
      if (json.sucesso && json.token) {
        console.log('\n🎉 LOGIN BEM-SUCEDIDO!');
        console.log('🎟️  Token:', json.token.substring(0, 50) + '...');
        console.log('👤 Usuário:', json.usuario?.email);
      } else {
        console.log('\n❌ Login falhou');
      }
    } catch (e) {
      console.log('\n📦 Response (raw):', body);
    }
  });
});

req.on('error', (e) => {
  console.error('❌ Erro:', e.message);
});

req.write(data);
req.end();
