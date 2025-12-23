+++
title = "IBB Kids App"
description = "Guia do aplicativo IBB Kids"
date = "2025-12-23"
draft = false
toc = false
categories = ["React", "Typescript", "Javascript"]
tags = ["React", "Typescript", "Javascript"]
image = "ibbkids.webp"
author = "Fabio M. Lopes"
+++

---

## PARTE 1: FUNDAÇÕES FRONTEND - REACT, TYPESCRIPT E VITE

### 1.1 O que é React?

React é uma biblioteca JavaScript para construir interfaces de usuário (UI) usando componentes reutilizáveis. Diferentemente de jQuery ou vanilla JavaScript que manipulam diretamente o DOM, React abstrai essa complexidade através de um conceito chamado **Virtual DOM**.

**Por que React?**
- **Componentes**: Você escreve pequenos blocos de UI reutilizáveis
- **Reatividade**: Quando dados mudam, a UI se atualiza automaticamente
- **Ecossistema**: Gigantesco conjunto de bibliotecas e ferramentas

Na sua aplicação IBB Kids, React é usado para:
- Formulários de login
- Seletor multi-etapa para professores (dia → horário → sala)
- Painel de administrador com CRUD de lições
- Notificações de sucesso/erro

**Estrutura Básica de um Componente React:**

```typescript
// Exemplo: Componente simples de botão
import React from 'react';

interface ButtonProps {
  label: string;
  onClick: () => void;
}

const Button: React.FC<ButtonProps> = ({ label, onClick }) => {
  return (
    <button onClick={onClick} className="px-4 py-2 bg-blue-500 text-white rounded">
      {label}
    </button>
  );
};

export default Button;
```

**Como isso funciona:**
1. O componente recebe `props` (propriedades) - dados que vêm de cima
2. Retorna JSX (JavaScript + XML) que parece HTML mas é JavaScript
3. O React transforma isso em elementos DOM reais
4. Quando as props mudam, o componente re-renderiza automaticamente

### 1.2 TypeScript - Segurança de Tipos

TypeScript adiciona **tipagem estática** ao JavaScript. Isso significa que você especifica qual tipo de dado cada variável deve ter antes mesmo de executar o código.

**Por que isso importa?**
- **Erros em tempo de desenvolvimento**: Você descobre problemas antes de rodar
- **Autocompletar**: Seu editor sabe exatamente qual propriedade você quer acessar
- **Documentação**: O código fica autodocumentado com os tipos

Na aplicação IBB Kids, veja como é usado:

```typescript
// Em src/types.ts - Define estrutura de dados
interface Lesson {
  id: number;
  day: string;           // "Segunda", "Terça", etc
  time: string;          // "09:00", "14:00"
  room: string;          // "Sala A", "Sala B"
  date: string;          // "2025-01-15"
  theme: string;         // Tema da aula
  prof_link?: string;    // Link do SharePoint para professor
  parents_link?: string; // Link para pais
}

// Agora quando você usa isso:
const lesson: Lesson = {
  id: 1,
  day: "Segunda",
  time: "09:00",
  // TypeScript avisa se você esquecer algum campo obrigatório!
};
```

**Benefício prático**: Se você tentar fazer `lesson.prof_link.toUpperCase()` sem verificar se existe, TypeScript avisa que pode ser `undefined`. Isso evita bugs clássicos em JavaScript.

### 1.3 Vite - Build Tool Moderno

Vite é uma ferramenta que:
1. **Durante desenvolvimento**: Serve arquivos rapidamente sem fazer bundle
2. **Para produção**: Compila tudo em arquivos otimizados

**Como funciona:**
- Quando você roda `npm run dev`, Vite inicia um servidor na porta 3000
- Qualquer mudança em arquivo `.ts` ou `.tsx` recarrega instantaneamente (HMR - Hot Module Replacement)
- Quando você faz `npm run build`, Vite compila React + TypeScript em HTML/CSS/JS otimizados

**Arquivo de configuração (`vite.config.ts`):**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    // Proxy para redirecionar requisições /api para o servidor Express
    proxy: {
      '/api': 'http://localhost:5000'
    }
  }
})
```

Este arquivo diz ao Vite:
- Use o plugin React (entende JSX)
- Rode na porta 3000
- Redirecione chamadas `/api` para o servidor Express

### 1.4 Tailwind CSS - Estilo Utility-First

Tailwind CSS não é um framework tradicional de temas. Você escreve estilos diretamente no HTML usando classes:

```tsx
// Em vez de escrever CSS:
// .button { padding: 8px 16px; background-color: #3b82f6; color: white; }

// Com Tailwind você escreve:
<button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
  Clique aqui
</button>
```

**Por que é bom:**
- Estilos colocalizados com HTML (sem ir para arquivo CSS distante)
- Temas consistentes (cores, espaçamentos definidos no `tailwind.config.js`)
- Arquivo final é menor porque remove classes não usadas

**Estrutura de classes Tailwind:**
- `px-4` = padding horizontal de 16px
- `bg-blue-500` = cor azul (existe 50 até 950)
- `hover:bg-blue-600` = muda ao passar mouse
- `rounded` = border-radius padrão

## PARTE 2: BACKEND - EXPRESS.JS E API REST

### 2.1 O que é Express.js?

Express é um framework minimalista para Node.js que facilita criar servidores web. Ele gerencia:
- **Rotas**: O que fazer quando uma requisição chega em `/api/lessons`
- **Middleware**: Processar requisições antes de chegar na rota (autenticação, log, etc)
- **Respostas**: Retornar JSON, HTML, arquivos, etc

**Na aplicação IBB Kids**, Express serve:
- A API pública de lições (sem autenticação)
- A API de administrador (protegida por JWT)
- Os arquivos estáticos (HTML/CSS/JS compilado do React)

### 2.2 Anatomia do Servidor Express

Veja a estrutura básica em `server/index.ts`:

```typescript
import express, { Request, Response } from 'express';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcrypt';

const app = express();

// Middleware para parsear JSON
app.use(express.json());

// Middleware customizado - verifica JWT e autorização
const authenticate = (req: Request, res: Response, next: Function) => {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Token não fornecido' });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!);
    req.user = decoded; // Anexa usuário à requisição
    next();
  } catch (error) {
    res.status(401).json({ error: 'Token inválido' });
  }
};

// ROTA PÚBLICA: Buscar lições
app.get('/api/lessons', (req: Request, res: Response) => {
  const { day, time, room } = req.query;
  
  // Query ao banco de dados com filtros
  const lessons = db.prepare(
    'SELECT * FROM lessons WHERE day = ? AND time = ? AND room = ?'
  ).all(day, time, room);
  
  res.json(lessons);
});

// ROTA PROTEGIDA: Criar lição (apenas admin)
app.post('/api/admin/lessons', authenticate, (req: Request, res: Response) => {
  // Aqui você sabe que o usuário foi autenticado
  const { day, time, room, date, theme, prof_link, parents_link } = req.body;
  
  const result = db.prepare(
    'INSERT INTO lessons (day, time, room, date, theme, prof_link, parents_link) VALUES (?, ?, ?, ?, ?, ?, ?)'
  ).run(day, time, room, date, theme, prof_link, parents_link);
  
  res.status(201).json({ id: result.lastInsertRowid, ...req.body });
});

// Iniciar servidor na porta 3000
app.listen(3000, () => {
  console.log('Servidor rodando em http://localhost:3000');
});
```

**O que acontece aqui passo a passo:**

1. Quando alguém faz GET em `/api/lessons?day=Segunda&time=09:00&room=SalaA`:
   - Express matcheia a rota `/api/lessons`
   - Extrai os parâmetros de query
   - Executa a query no banco de dados
   - Retorna JSON com as lições

2. Quando alguém faz POST em `/api/admin/lessons` com um token JWT:
   - Express passa pelo middleware `authenticate`
   - Se o token for inválido, retorna erro 401
   - Se válido, continua e insere a lição
   - Retorna a lição criada com id 201 (Created)

### 2.3 Fluxo de uma Requisição

```
1. FRONTEND (React)
   └─> fetch('/api/lessons?day=Segunda&time=09:00&room=SalaA')

2. NAVEGADOR
   └─> Faz requisição HTTP GET

3. SERVIDOR NGINX
   └─> Recebe requisição e faz proxy para http://localhost:3000

4. EXPRESS
   ├─> Identifica rota: GET /api/lessons
   ├─> Extrai parâmetros: day, time, room
   ├─> Query banco de dados
   └─> Retorna JSON com lições

5. NAVEGADOR
   ├─> Recebe resposta JSON
   └─> Renderiza as lições no React

6. TELA DO PROFESSOR
   └─> Mostra lições do dia/hora/sala
```

## PARTE 3: BANCO DE DADOS - SQLITE

### 3.1 O que é SQLite?

SQLite é um banco de dados SQL que:
- **Roda localmente**: Não precisa de servidor separado
- **Arquivo único**: Toda a base fica em um arquivo `.db`
- **Rápido**: Ótimo para aplicações pequenas/médias
- **Sem dependências**: Não precisa instalar MySQL ou PostgreSQL

Na IBB Kids, o banco está em `data/lessons.db` no servidor.

### 3.2 Schema do Banco

O schema é a "planta" de como os dados são organizados:

```sql
CREATE TABLE lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT NOT NULL,
    time TEXT NOT NULL,
    room TEXT NOT NULL,
    date TEXT NOT NULL,
    theme TEXT NOT NULL,
    prof_link TEXT,
    parents_link TEXT
);

CREATE INDEX idx_day_time_room ON lessons(day, time, room);
```

**O que significa cada parte:**

- `id INTEGER PRIMARY KEY AUTOINCREMENT`: Identificador único que aumenta automaticamente (1, 2, 3...)
- `day TEXT NOT NULL`: Dia da semana, obrigatório
- `prof_link TEXT`: Link do professor, **opcional** (pode ser NULL)
- `CREATE INDEX`: Cria índice para buscas mais rápidas

**Por que o índice importa:**
- Quando um professor faz login e seleciona "Segunda, 09:00, Sala A"
- Em vez de varrer 10.000 lições procurando, o índice localiza em milissegundos
- É como um índice de livro: você não lê cada página procurando

### 3.3 Operações Básicas com SQLite

A aplicação usa `better-sqlite3`, que é uma lib de alto desempenho para Node.js:

```typescript
import Database from 'better-sqlite3';

const db = new Database('data/lessons.db');

// CREATE - Inserir nova lição
const insertStmt = db.prepare(
  'INSERT INTO lessons (day, time, room, date, theme) VALUES (?, ?, ?, ?, ?)'
);
insertStmt.run('Segunda', '09:00', 'Sala A', '2025-01-20', 'Alfabeto');

// READ - Buscar lições
const selectStmt = db.prepare(
  'SELECT * FROM lessons WHERE day = ? AND time = ?'
);
const lessons = selectStmt.all('Segunda', '09:00');

// UPDATE - Atualizar lição
const updateStmt = db.prepare(
  'UPDATE lessons SET theme = ? WHERE id = ?'
);
updateStmt.run('Números', 1);

// DELETE - Deletar lição
const deleteStmt = db.prepare('DELETE FROM lessons WHERE id = ?');
deleteStmt.run(1);
```

**Padrão de segurança importante:**
- Nunca faça: `SELECT * FROM lessons WHERE day = '${day}'` (SQL Injection!)
- Sempre use: `SELECT * FROM lessons WHERE day = ?` com valores após (PreparedStatement)
- O `?` é substituído de forma segura

### 3.4 Migrações de Dados

Quando você precisa alterar o schema (adicionar coluna, mudar tipo, etc), é necessário uma "migração". Na IBB Kids há exemplos:

- `MIGRATION_GUIDE.pt-br.md`: Guia para mover senhas de variáveis de ambiente para banco de dados
- `server/seed.ts`: Popula o banco com dados iniciais do objeto `BANCO_DE_DADOS`

**Exemplo: Se você quisesse adicionar campo "duracao_minutos":**

1. Atualizar `server/db.ts`:
```typescript
// Adicionar coluna
ALTER TABLE lessons ADD COLUMN duracao_minutos INTEGER DEFAULT 45;
```

2. Atualizar interface TypeScript em `src/types.ts`:
```typescript
interface Lesson {
  // ... campos existentes
  duracao_minutos?: number; // novo campo
}
```

3. Atualizar seed em `server/seed.ts` para popular esse campo

4. Atualizar frontend para mostrar/editar esse campo

## PARTE 4: AUTENTICAÇÃO E SEGURANÇA

### 4.1 JWT (JSON Web Tokens)

JWT é um padrão para autenticação sem armazenar sessão no servidor.

**Como funciona:**

```
1. USUÁRIO FAZ LOGIN
   ├─> Envia username + senha
   ├─> Servidor valida credenciais no banco
   └─> Se válida, gera token JWT

2. SERVIDOR GERA TOKEN
   └─> Token contém: { userId: 1, role: 'admin', exp: 1234567890 }
       (Codificado em Base64 + assinado com JWT_SECRET)

3. TOKEN RETORNA AO CLIENTE
   └─> Frontend armazena em localStorage/sessionStorage

4. REQUISIÇÕES FUTURAS
   ├─> Frontend envia: Authorization: Bearer eyJhbGc...
   ├─> Servidor valida assinatura com JWT_SECRET
   ├─> Se válido, prossegue
   └─> Se inválido ou expirado, retorna 401
```

**Implementação na IBB Kids:**

```typescript
// Login
app.post('/api/login', (req: Request, res: Response) => {
  const { password, role } = req.body;
  
  // Verifica senha (bcrypt - explicado abaixo)
  const isValid = bcrypt.compareSync(password, storedHash);
  
  if (!isValid) {
    return res.status(401).json({ error: 'Senha incorreta' });
  }
  
  // Gera token com validade de 12 horas
  const token = jwt.sign(
    { role, userId: 1 },
    process.env.JWT_SECRET!,
    { expiresIn: '12h' }
  );
  
  res.json({ token });
});

// No frontend, armazena:
localStorage.setItem('token', token);

// Em requisições posteriores:
const token = localStorage.getItem('token');
fetch('/api/admin/lessons', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### 4.2 Bcrypt - Hashing de Senhas

Bcrypt é algoritmo para **não armazenar senhas em texto plano** no banco.

**Por que não armazenar texto plano?**
- Se hacker acessa banco, não vê senhas
- Cada senha gera hash diferente mesmo tendo o mesmo texto
- É matemático: impossível recuperar senha original do hash

**Como funciona:**

```typescript
import bcrypt from 'bcrypt';

// REGISTRAR USUÁRIO OU ALTERAR SENHA
const senha = 'MinhaSenh@123';
const hash = bcrypt.hashSync(senha, 10); // Resultado: $2b$10$...

// Armazenar no banco:
db.prepare(
  'UPDATE users SET senha_hash = ? WHERE id = ?'
).run(hash, userId);

// FAZER LOGIN
const senhaFornecida = 'MinhaSenh@123';
const hashArmazenado = '$2b$10$...'; // Do banco

const isValid = bcrypt.compareSync(senhaFornecida, hashArmazenado);
// Retorna true/false

if (isValid) {
  // Login bem-sucedido
}
```

**O "10" em `bcrypt.hashSync(senha, 10)`?**
- É o "salt rounds" - quantas vezes o algoritmo roda
- Maior número = mais seguro mas mais lento
- 10 é o padrão recomendado

### 4.3 Sistema de Funções (Role-Based Access)

Na IBB Kids, há dois papéis: `professor` e `admin`.

```typescript
interface User {
  userId: number;
  role: 'professor' | 'admin';
}

// Middleware que verifica se é admin
const requireAdmin = (req: Request, res: Response, next: Function) => {
  const user = req.user as User;
  
  if (user.role !== 'admin') {
    return res.status(403).json({ error: 'Acesso negado' });
  }
  
  next();
};

// Aplicar em rotas:
app.delete(
  '/api/admin/lessons/:id',
  authenticate,
  requireAdmin,
  (req: Request, res: Response) => {
    // Apenas admins chegam aqui
  }
);
```

**Fluxo de acesso:**
1. Usuário faz requisição a `/api/admin/lessons/1`
2. Middleware `authenticate` valida token
3. Middleware `requireAdmin` verifica se role é 'admin'
4. Se passar nos dois, pode deletar

### 4.4 Mudança de Senha Autônoma

A aplicação possui sistema para usuários mudarem senha sem acesso SSH:

```typescript
// Rota: POST /api/change-password
app.post('/api/change-password', authenticate, (req: Request, res: Response) => {
  const { senhaAtual, senhaNova } = req.body;
  const user = req.user as User;
  
  // 1. Verifica se senha atual está correta
  const senhaAtualHash = db.prepare(
    'SELECT senha_hash FROM users WHERE id = ?'
  ).get(user.userId);
  
  const isValid = bcrypt.compareSync(senhaAtual, senhaAtualHash.senha_hash);
  if (!isValid) {
    return res.status(401).json({ error: 'Senha atual incorreta' });
  }
  
  // 2. Hash da nova senha
  const novoHash = bcrypt.hashSync(senhaNova, 10);
  
  // 3. Atualiza no banco
  db.prepare(
    'UPDATE users SET senha_hash = ? WHERE id = ?'
  ).run(novoHash, user.userId);
  
  res.json({ message: 'Senha alterada com sucesso' });
});
```

## PARTE 5: IMPLANTAÇÃO - PM2, NGINX E GITHUB ACTIONS

### 5.1 PM2 - Process Manager

PM2 garante que sua aplicação:
- **Inicia automaticamente** quando o servidor reinicia
- **Reinicia se cair** (crash recovery)
- **Gerencia logs** de erros
- **Permite múltiplas instâncias** (load balancing)

**Arquivo de configuração (`ecosystem.config.js`):**

```javascript
module.exports = {
  apps: [
    {
      name: 'ibb-kids-api',
      script: './dist/server/index.js',
      instances: 1,           // Usar 1 processo
      exec_mode: 'cluster',   // Modo cluster se usar múltiplas instâncias
      env: {
        NODE_ENV: 'production',
        JWT_SECRET: 'seu_secret_aqui',
        TEACHER_PASSWORD: 'senha_professor',
        ADMIN_PASSWORD: 'senha_admin'
      },
      error_file: 'logs/error.log',
      out_file: 'logs/out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
```

**Comandos PM2 úteis:**

```bash
# Iniciar a aplicação
pm2 start ecosystem.config.js

# Ver status de todos os processos
pm2 status

# Ver logs em tempo real
pm2 logs ibb-kids-api

# Reiniciar aplicação
pm2 restart ibb-kids-api

# Parar aplicação
pm2 stop ibb-kids-api

# Salvar configuração para auto-start no boot
pm2 startup
pm2 save
```

### 5.2 Nginx - Reverse Proxy

Nginx é um servidor web que:
- **Recebe requisições** na porta 80 (HTTP) e 443 (HTTPS)
- **Faz proxy** para sua aplicação Node.js na porta 3000
- **Serve arquivos estáticos** de forma muito eficiente
- **Comprime respostas** (gzip)

**Configuração Nginx típica (`/etc/nginx/sites-available/ibb-kids`):**

```nginx
server {
    listen 80;
    server_name seu-dominio.com.br;
    
    # Redirecionar HTTP para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com.br;
    
    # Certificados SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com.br/privkey.pem;
    
    # Servir arquivos estáticos do React build
    location / {
        root /var/www/ibb-kids/dist;
        try_files $uri /index.html;
    }
    
    # Proxy para API Express
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

**O que acontece:**

```
Cliente                Nginx                Node.js Express
(Navegador)         (Porta 80/443)        (Porta 3000)
    |                    |                       |
    |-- GET / ---------->|                       |
    |                    |-- (arquivo dist/)    |
    |<-- HTML/CSS/JS ----|                      |
    |                    |                       |
    |-- GET /api/lessons-|                       |
    |                    |-- GET /api/lessons -->|
    |                    |<-- JSON ------------<|
    |<-- JSON ----------|                       |
```

**SELinux no Oracle Linux:**
A documentação menciona que é necessário configurar SELinux para Nginx se conectar ao localhost:3000. Comando típico:

```bash
# Permite Nginx fazer conexões de rede
sudo setsebool -P httpd_can_network_connect on

# Verifica status
getsebool httpd_can_network_connect
```

### 5.3 GitHub Actions - CI/CD

GitHub Actions automática:
1. **Testa** código em cada push
2. **Compila** TypeScript e React
3. **Faz deploy** para servidor Oracle Linux

**Workflow file (`.github/workflows/deploy.yml`):**

```yaml
name: Deploy IBB Kids

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm install
      
      - name: Build project
        run: npm run build
      
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_KEY }}
          script: |
            cd /home/ubuntu/ibb-kids
            git pull origin main
            npm install
            npm run build
            pm2 restart ibb-kids-api
```

**Como funciona:**
1. Você faz `git push` para `main`
2. GitHub Actions dispara automaticamente
3. Compila tudo em um servidor Ubuntu temporário
4. Faz SSH para seu servidor Oracle Linux
5. Puxa código, compila e reinicia com PM2

**Secrets necessários:**
- `DEPLOY_HOST`: IP do servidor (ex: 123.45.67.89)
- `DEPLOY_USER`: Usuário SSH (ex: ubuntu)
- `DEPLOY_KEY`: Chave SSH privada

## PARTE 6: INTEGRAÇÃO - COMO TUDO FUNCIONA JUNTO

### 6.1 Fluxo Completo: Professor Acessando Lições

```
PASSO 1: PROFESSOR ACESSA http://seu-dominio.com.br
┌─────────────────────────────────────────────────────┐
│ Nginx recebe requisição na porta 80                  │
│ ↓                                                     │
│ Redireciona para HTTPS (443)                         │
│ ↓                                                     │
│ Serve arquivo /dist/index.html (React compilado)   │
└─────────────────────────────────────────────────────┘

PASSO 2: PROFESSOR VÊ TELA DE LOGIN
┌─────────────────────────────────────────────────────┐
│ React carrega em navegador                           │
│ Componente App.tsx renderiza <LoginPage />          │
│ Tailwind CSS aplica estilo                           │
└─────────────────────────────────────────────────────┘

PASSO 3: PROFESSOR DIGITA SENHA E CLICA "LOGIN"
┌─────────────────────────────────────────────────────┐
│ React captura evento onClick                         │
│ ↓                                                     │
│ JavaScript faz fetch POST /api/login                │
│ ↓                                                     │
│ Nginx faz proxy para localhost:3000                 │
└─────────────────────────────────────────────────────┘

PASSO 4: SERVIDOR EXPRESS PROCESSA LOGIN
┌─────────────────────────────────────────────────────┐
│ app.post('/api/login') recebe requisição           │
│ ↓                                                     │
│ Valida senha com bcrypt.compareSync()              │
│ ↓                                                     │
│ Se válida, jwt.sign() gera token com validade 12h │
│ ↓                                                     │
│ Retorna { token: "eyJhbGc..." }                    │
└─────────────────────────────────────────────────────┘

PASSO 5: FRONTEND ARMAZENA TOKEN E NAVEGA
┌─────────────────────────────────────────────────────┐
│ React recebe token                                   │
│ localStorage.setItem('token', token)               │
│ ↓                                                     │
│ Renderiza seletor: Dia → Horário → Sala            │
└─────────────────────────────────────────────────────┘

PASSO 6: PROFESSOR SELECIONA DIA, HORÁRIO, SALA
┌─────────────────────────────────────────────────────┐
│ React captura seleção                               │
│ ↓                                                     │
│ fetch GET /api/lessons?day=Segunda&time=09:00&room=SalaA
│ ↓                                                     │
│ Nginx faz proxy                                      │
│ ↓                                                     │
│ Express recebe em app.get('/api/lessons')          │
└─────────────────────────────────────────────────────┘

PASSO 7: EXPRESS CONSULTA BANCO DE DADOS
┌─────────────────────────────────────────────────────┐
│ db.prepare('SELECT * FROM lessons WHERE...').all()│
│ ↓                                                     │
│ SQLite usa índice idx_day_time_room para            │
│ encontrar lições em milissegundos                  │
│ ↓                                                     │
│ Retorna array de lições                             │
│ ↓                                                     │
│ res.json(lessons) envia JSON para frontend         │
└─────────────────────────────────────────────────────┘

PASSO 8: FRONTEND RENDERIZA LIÇÕES
┌─────────────────────────────────────────────────────┐
│ React recebe JSON                                    │
│ State é atualizado: useState(lessons)              │
│ ↓                                                     │
│ Component re-renderiza com Tailwind CSS            │
│ ↓                                                     │
│ Professor vê lições com temas e links do           │
│ SharePoint em menos de 1 segundo                   │
└─────────────────────────────────────────────────────┘
```

### 6.2 Fluxo Completo: Admin Criando Lição

```
PASSO 1-5: [Igual ao fluxo de professor acima]

PASSO 6: ADMIN VÊ PAINEL COM FORM
┌─────────────────────────────────────────────────────┐
│ React renderiza <AdminPanel />                      │
│ Modal com campos: day, time, room, theme, links   │
└─────────────────────────────────────────────────────┘

PASSO 7: ADMIN PREENCHE FORM E CLICA "SALVAR"
┌─────────────────────────────────────────────────────┐
│ React captura valores do formulário                 │
│ ↓                                                     │
│ fetch POST /api/admin/lessons                      │
│ Headers: { Authorization: `Bearer ${token}` }     │
│ Body: { day, time, room, date, theme, links }    │
└─────────────────────────────────────────────────────┘

PASSO 8: EXPRESS VALIDA AUTENTICAÇÃO
┌─────────────────────────────────────────────────────┐
│ Middleware authenticate é executado                 │
│ ↓                                                     │
│ jwt.verify(token, JWT_SECRET) valida assinatura   │
│ ↓                                                     │
│ Se inválido/expirado: retorna 401                  │
│ Se válido: anexa user ao req e prossegue          │
└─────────────────────────────────────────────────────┘

PASSO 9: EXPRESS INSERE NO BANCO
┌─────────────────────────────────────────────────────┐
│ db.prepare('INSERT INTO lessons...').run(...)     │
│ ↓                                                     │
│ SQLite cria novo registro                           │
│ ↓                                                     │
│ Retorna { id: 123, day, time, room, ... }        │
└─────────────────────────────────────────────────────┘

PASSO 10: FRONTEND ATUALIZA LISTA
┌─────────────────────────────────────────────────────┐
│ React recebe lição criada                           │
│ Adiciona à lista com setLessons([...oldLessons, newLesson])
│ ↓                                                     │
│ AdminPanel re-renderiza com nova lição              │
│ Modal fecha, notificação "Lição criada!"           │
└─────────────────────────────────────────────────────┘
```

### 6.3 Ciclo de Desenvolvimento

```
SEU COMPUTADOR (Desenvolvimento Local)
├─ npm run dev
│  ├─ Vite dev server na porta 3000
│  ├─ Express server na porta 3000 (compilado em tempo real)
│  ├─ HMR (Hot Module Replacement) recarrega React automaticamente
│  └─ Browser DevTools mostra TypeScript original (sourcemaps)
│
├─ Editar arquivo (ex: src/App.tsx)
│  └─ Vite detecta mudança
│     └─ HMR recarrega apenas o componente
│        └─ Browser atualiza em <100ms
│
└─ Tudo parece funcionar localmente

SEU REPOSITÓRIO GIT
├─ git add .
├─ git commit -m "Adiciona validação de form"
└─ git push origin main

GITHUB ACTIONS
├─ Trigger: detecta push para main
├─ npm install (instala dependências)
├─ npm run build
│  ├─ tsc (compila TypeScript em JavaScript)
│  └─ vite build (compila React em HTML/CSS/JS otimizado)
├─ Resultados em /dist
│  ├─ dist/server/index.js (Express compilado)
│  └─ dist/index.html, dist/assets/*.js (React)
└─ SSH para seu servidor Oracle Linux

SEU SERVIDOR ORACLE LINUX
├─ cd /home/ubuntu/ibb-kids
├─ git pull origin main
├─ npm install (pode ter novas dependências)
├─ npm run build (compila localmente novamente)
├─ pm2 restart ibb-kids-api (reinicia com novo código)
└─ Nginx já está servindo, redireciona para novo código

PROFESSORES ACESSAM
├─ http://seu-dominio.com.br
└─ Veem versão nova da aplicação!
```

## PARTE 7: TAREFAS COMUNS DE MANUTENÇÃO

### 7.1 Adicionar Novo Campo de Lição

**Cenário:** Você quer adicionar campo "duração_minutos"

```
PASSO 1: Atualizar banco de dados (server/db.ts)
─────────────────────────────────────────────
// server/db.ts
db.exec(`
  ALTER TABLE lessons ADD COLUMN duracao_minutos INTEGER DEFAULT 45;
`);

PASSO 2: Atualizar tipos TypeScript (src/types.ts)
──────────────────────────────────────────────────
interface Lesson {
  id: number;
  day: string;
  time: string;
  room: string;
  date: string;
  theme: string;
  prof_link?: string;
  parents_link?: string;
  duracao_minutos?: number;  // ← NOVO CAMPO
}

PASSO 3: Atualizar seed (server/seed.ts)
─────────────────────────────────────────
// Adicionar duracao_minutos ao objeto BANCO_DE_DADOS
{
  day: 'Segunda',
  time: '09:00',
  room: 'Sala A',
  date: '2025-01-20',
  theme: 'Alfabeto',
  duracao_minutos: 45  // ← NOVO CAMPO
}

PASSO 4: Atualizar seed.ts para inserir valor
──────────────────────────────────────────────
// Na função de semeadura
const insertLesson = db.prepare(`
  INSERT INTO lessons (day, time, room, date, theme, prof_link, parents_link, duracao_minutos)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?)
`);

PASSO 5: Atualizar AdminPanel.tsx
──────────────────────────────────
// Adicionar input no formulário
<input
  type="number"
  value={formData.duracao_minutos || 45}
  onChange={(e) => setFormData({
    ...formData,
    duracao_minutos: parseInt(e.target.value)
  })}
  placeholder="Duração (minutos)"
/>

PASSO 6: Fazer deploy
─────────────────────
git add .
git commit -m "Adiciona campo duracao_minutos"
git push origin main
# GitHub Actions deploya automaticamente

PASSO 7: Executar seed no servidor (se necessário resetar dados)
────────────────────────────────────────────────────────────────
# Via SSH no servidor
cd /home/ubuntu/ibb-kids
npm run seed
```

### 7.2 Alterar Senha de Usuário

**Cenário:** Admin esqueceu a senha

```
OPÇÃO 1: Usuário muda própria senha (RECOMENDADO)
─────────────────────────────────────────────────
1. Fazer login com senha atual
2. Clicar no menu "Opções"
3. Selecionar "🔒 Mudar Senha"
4. Seguir assistente (consulte PASSWORD_CHANGE_GUIDE.pt-br.md)

OPÇÃO 2: Redefinir via banco de dados (admin do servidor)
───────────────────────────────────────────────────────────
$ sqlite3 data/lessons.db

sqlite> SELECT * FROM users;
┌────┬──────────┬─────────────────────────────────────────┐
│ id │ role     │ senha_hash                              │
├────┼──────────┼─────────────────────────────────────────┤
│ 1  │ teacher  │ $2b$10$... (hash bcrypt)               │
│ 2  │ admin    │ $2b$10$... (hash bcrypt)               │
└────┴──────────┴─────────────────────────────────────────┘

# Não consegue reverter hash bcrypt, precisa gerar novo
# Use Node.js:

$ node
> const bcrypt = require('bcrypt');
> bcrypt.hashSync('NovaSenha123', 10);
'$2b$10$...'

# Copiar hash e atualizar:
sqlite> UPDATE users SET senha_hash = '$2b$10$...' WHERE id = 2;
sqlite> .quit

# Reiniciar servidor
pm2 restart ibb-kids-api
```

### 7.3 Visualizar Logs do Servidor

```bash
# Ver logs em tempo real
pm2 logs ibb-kids-api

# Ver apenas últimas 100 linhas
pm2 logs ibb-kids-api --lines 100

# Ver logs de erro
pm2 logs ibb-kids-api --err

# Limpar logs
pm2 flush

# Ver status geral
pm2 status

# Ver detalhes da aplicação
pm2 show ibb-kids-api
```

### 7.4 Fazer Backup do Banco de Dados

```bash
# Via SSH no servidor Oracle Linux

# Copiar arquivo do banco para seu computador
scp ubuntu@seu-ip:/home/ubuntu/ibb-kids/data/lessons.db ./lessons-backup-$(date +%Y%m%d).db

# Ou fazer backup local no servidor
cp data/lessons.db data/lessons.db.backup

# Ver tamanho do banco
ls -lh data/lessons.db

# Verificar integridade do banco
sqlite3 data/lessons.db "PRAGMA integrity_check;"
```

### 7.5 Monitorar Performance

```bash
# CPU e memória usada pela aplicação
pm2 monit

# Saída esperada:
# ┌─────────────┬─────────┬────────┬─────────┬──────────┬─────────┐
# │ Name        │ PID     │ CPU %  │ Memory  │ Restarted│ Uptime  │
# ├─────────────┼─────────┼────────┼─────────┼──────────┼─────────┤
# │ ibb-kids-api│ 12345   │ 0.5%   │ 45 MB   │ 0        │ 5 days  │
# └─────────────┴─────────┴────────┴─────────┴──────────┴─────────┘

# Ver histórico de restarts
pm2 web  # Abre dashboard na porta 9615

# Ver se há memory leaks
# Se memória crescer constantemente sem resetar, há problema
```

## PARTE 8: TROUBLESHOOTING

### Problema: "Port 3000 already in use"

```bash
# Encontrar processo usando porta 3000
lsof -i :3000
# ou em Windows
netstat -ano | findstr :3000

# Matar processo
kill -9 PID
# ou em Windows
taskkill /PID PID /F

# Ou usar porta diferente em vite.config.ts
server: {
  port: 3001  // Porta alternativa
}
```

### Problema: "Cannot GET /"

```
Causa: Nginx não está proxy passando corretamente
Solução:

1. Verificar se Express está rodando:
   pm2 logs ibb-kids-api

2. Verificar configuração Nginx:
   sudo nginx -t

3. Recarregar Nginx:
   sudo systemctl reload nginx

4. Testar conexão local:
   curl http://localhost:3000
```

### Problema: "Unauthorized" ao fazer requisição admin

```
Causa: Token JWT inválido/expirado
Solução:

1. Fazer login novamente para renovar token
   (Tokens expiram após 12h)

2. Verificar se JWT_SECRET está igual no servidor
   cat .env | grep JWT_SECRET

3. Se mudou JWT_SECRET, todos os tokens antigos viram inválidos
   (Usuários precisam fazer login novamente)
```

### Problema: "Database is locked"

```
Causa: SQLite sendo acessado por múltiplos processos simultaneamente
Solução:

1. Usar apenas 1 instância Node.js (não clusters)
   instances: 1 em ecosystem.config.js

2. Se tiver múltiplos servidores, considerar PostgreSQL

3. Aumentar timeout:
   const db = new Database('data/lessons.db');
   db.pragma('journal_mode = WAL');  // Write-Ahead Logging
```

---

## RESUMO DE TECNOLOGIAS

| Camada | Tecnologia | Função |
|--------|-----------|--------|
| **Frontend** | React 18 | Biblioteca de UI com componentes reativos |
| | TypeScript | Tipagem estática para segurança |
| | Vite | Build tool rápido e servidor dev |
| | Tailwind CSS | Estilos utility-first |
| **Backend** | Express.js | Framework web Node.js |
| | TypeScript | Tipagem no servidor também |
| | JWT | Autenticação sem estado |
| | bcrypt | Hash seguro de senhas |
| **Database** | SQLite | Banco de dados local |
| | better-sqlite3 | Driver rápido e síncrono |
| **Implantação** | PM2 | Gerenciador de processos Node.js |
| | Nginx | Reverse proxy e servidor web |
| | GitHub Actions | CI/CD automática |
| | Oracle Linux | Sistema operacional do servidor |

---

## PRÓXIMOS PASSOS PARA APRENDIZADO

1. **Entender React em profundidade**
   - Hooks (useState, useEffect, useContext)
   - Renderização condicional
   - Formulários e validação

2. **Aprofundar Express.js**
   - Erro handling robusto
   - Rate limiting
   - CORS e segurança

3. **Otimizar banco de dados**
   - Mais índices estratégicos
   - Queries complexas com JOINs
   - Migrar para PostgreSQL se escalar

4. **Segurança em produção**
   - HTTPS/SSL (Let's Encrypt)
   - CORS adequado
   - Rate limiting
   - Validação rigorosa de entrada

5. **Monitoramento e alertas**
   - Sentry para rastrear erros
   - CloudWatch ou Prometheus para métricas
   - Alertas se aplicação cair

---

**Conclusão**: Você agora entende cada tecnologia usada na IBB Kids, como elas se conectam e como manter a aplicação funcionando. A chave é praticar regularmente com deploy, logs e troubleshooting.
