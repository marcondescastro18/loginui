const { Client } = require('pg');

const client = new Client({
  host: 'login_login-aut-db',
  port: 5432,
  user: 'postgres',
  password: 'fa0e7201e1773b163eb3',
  database: 'auth_db'
});

async function listAllTables() {
  try {
    await client.connect();
    console.log('✅ Conectado ao banco de dados\n');
    console.log('=' .repeat(80));
    console.log('📊 ESTRUTURA DO BANCO DE DADOS');
    console.log('=' .repeat(80));
    
    // Listar todas as tabelas
    const tablesResult = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      ORDER BY table_name
    `);
    
    console.log(`\n🗂️  Total de tabelas: ${tablesResult.rows.length}\n`);
    
    // Para cada tabela, listar colunas
    for (const table of tablesResult.rows) {
      const tableName = table.table_name;
      console.log('─'.repeat(80));
      console.log(`📋 Tabela: ${tableName.toUpperCase()}`);
      console.log('─'.repeat(80));
      
      // Listar colunas da tabela
      const columnsResult = await client.query(`
        SELECT 
          column_name,
          data_type,
          character_maximum_length,
          is_nullable,
          column_default
        FROM information_schema.columns
        WHERE table_name = $1
        ORDER BY ordinal_position
      `, [tableName]);
      
      console.log('\nColunas:');
      columnsResult.rows.forEach((col, idx) => {
        const type = col.character_maximum_length 
          ? `${col.data_type}(${col.character_maximum_length})`
          : col.data_type;
        const nullable = col.is_nullable === 'YES' ? 'NULL' : 'NOT NULL';
        const defaultVal = col.column_default ? ` DEFAULT ${col.column_default}` : '';
        
        console.log(`  ${idx + 1}. ${col.column_name.padEnd(20)} ${type.padEnd(25)} ${nullable}${defaultVal}`);
      });
      
      // Contar registros
      const countResult = await client.query(`SELECT COUNT(*) FROM ${tableName}`);
      console.log(`\n📊 Total de registros: ${countResult.rows[0].count}`);
      
      // Mostrar alguns registros (máximo 3)
      const dataResult = await client.query(`SELECT * FROM ${tableName} LIMIT 3`);
      if (dataResult.rows.length > 0) {
        console.log('\n🔍 Primeiros registros:');
        dataResult.rows.forEach((row, idx) => {
          console.log(`\n  Registro ${idx + 1}:`);
          Object.entries(row).forEach(([key, value]) => {
            let displayValue = value;
            if (typeof value === 'string' && value.length > 50) {
              displayValue = value.substring(0, 47) + '...';
            }
            console.log(`    ${key}: ${displayValue}`);
          });
        });
      }
      console.log('\n');
    }
    
    console.log('=' .repeat(80));
    console.log('✅ Consulta concluída!');
    console.log('=' .repeat(80));
    
  } catch (err) {
    console.error('❌ Erro ao consultar banco:', err.message);
    console.error(err);
  } finally {
    await client.end();
  }
}

listAllTables();
