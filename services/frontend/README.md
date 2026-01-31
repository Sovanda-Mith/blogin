# Blogin Frontend

Vue.js 3 frontend for the Blogin microservices blogging platform.

## Features

- Vue 3 with Composition API and `<script setup>` syntax
- Vue Router for SPA navigation
- Pinia for state management
- Axios for API communication
- Markdown rendering with Marked
- JWT authentication with automatic token refresh
- Infinite scroll pagination
- Responsive design

## Project Structure

```
src/
├── api/           # Axios configuration
├── components/    # Vue components
├── router/        # Vue Router configuration
├── stores/        # Pinia stores
├── views/         # Page components
├── App.vue        # Root component
└── main.js        # Entry point
```

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8080
VITE_MEDIA_URL=http://localhost:9000
```

## Docker

```bash
# Development
docker build --target development -t blogin-frontend:dev .
docker run -p 3000:3000 blogin-frontend:dev

# Production
docker build --target production -t blogin-frontend .
docker run -p 80:80 blogin-frontend
```

## API Endpoints

The frontend expects these API endpoints:

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user
- `PUT /auth/profile` - Update profile

- `GET /posts` - List posts (paginated)
- `GET /posts/:slug` - Get single post
- `POST /posts` - Create post
- `PUT /posts/:slug` - Update post
- `DELETE /posts/:slug` - Delete post
- `POST /posts/:slug/like` - Like/unlike post

- `GET /posts/:id/comments` - Get comments
- `POST /posts/:id/comments` - Add comment
- `DELETE /posts/:id/comments/:commentId` - Delete comment

- `GET /users/:username` - Get user profile
- `GET /users/:username/posts` - Get user's posts
