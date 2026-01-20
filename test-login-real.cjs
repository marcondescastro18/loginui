const https = require('https');

const data = JSON.stringify({
  email: 'teste@email.com',
  senha: '123456'
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

console.log('🔐 Testando login...\n');

const req = https.request(options, (res) => {
  console.log(`📊 Status: ${res.statusCode}`);
  console.log(`📋 Headers:`, JSON.stringify(res.headers, null, 2));
  
  let body = '';
  res.on('data', (chunk) => body += chunk);
  res.on('end', () => {
    console.log('\n📦 Response Body:');
    try {
      const json = JSON.parse(body);
      console.log(JSON.stringify(json, null, 2));
      
      if (json.sucesso && json.token) {
        console.log('\n✅ LOGIN BEM-SUCEDIDO!');
        console.log('🎟️  Token recebido:', json.token.substring(0, 50) + '...');
      } else {
        console.log('\n❌ FALHA NO LOGIN');
      }
    } catch (e) {
      console.log(body);
    }
  });
});

req.on('error', (e) => {
  console.error('❌ Erro:', e.message);
});

req.write(data);
req.end();
