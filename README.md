# Blogin Microservices - Complete Implementation

## Project Overview

A full-featured blog platform built with Python FastAPI microservices and Vue.js frontend, designed for deployment on AWS ECS Fargate.

## Architecture

### Microservices

1. **Auth Service** (`:8001`) - JWT authentication, registration, login, token refresh
2. **User Service** (`:8002`) - User profile management, username handling
3. **Post Service** (`:8003`) - Blog posts, tags, search, pagination
4. **Comment Service** (`:8004`) - Nested comments with soft delete
5. **Like Service** (`:8005`) - Like/unlike functionality
6. **Gateway** (`:8080`) - Nginx reverse proxy with path-based routing
7. **Frontend** (`:3000`) - Vue.js 3 SPA with composition API

### Technology Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, PostgreSQL 15
- **Frontend**: Vue.js 3, Vite, Pinia, Vue Router, Axios
- **Infrastructure**: Docker, Docker Compose, AWS ECS Fargate, Terraform
- **CI/CD**: GitHub Actions

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Make (optional, for convenience commands)
- AWS CLI (for deployment)

### Local Development

```bash
# Clone the repository
git clone <repo-url>
cd blogin

# Copy environment variables
cp .env.example .env

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec postgres psql -U blogin_user -d blogin -f /docker-entrypoint-initdb.d/init-db.sh
# Or
make migrate

# View logs
make logs

# Stop services
make down
```

### Access the Application

- **Frontend**: http://localhost:8080
- **API Gateway**: http://localhost:8080/api/
- **Individual Services**:
  - Auth Service: http://localhost:8001
  - User Service: http://localhost:8002
  - Post Service: http://localhost:8003
  - Comment Service: http://localhost:8004
  - Like Service: http://localhost:8005

## API Documentation

### Authentication

All protected endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Endpoints

#### Auth Service
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout and revoke token
- `GET /auth/me` - Get current user
- `GET /auth/verify` - Verify token validity

#### User Service
- `GET /users/profiles` - List all profiles (paginated)
- `GET /users/profiles/search?q={query}` - Search profiles
- `GET /users/profiles/{username}` - Get profile by username
- `POST /users/profiles` - Create profile (requires auth)
- `PUT /users/profiles/me` - Update my profile (requires auth)
- `DELETE /users/profiles/me` - Delete my profile (requires auth)
- `GET /users/me` - Get my profile (requires auth)

#### Post Service
- `GET /posts` - List posts (paginated, filterable)
- `GET /posts/{slug}` - Get single post
- `POST /posts` - Create post (requires auth)
- `PUT /posts/{post_id}` - Update post (requires auth, owner only)
- `DELETE /posts/{post_id}` - Delete post (requires auth, owner only)
- `GET /tags` - List all tags
- `GET /authors/{author_id}/posts` - Get posts by author

#### Comment Service
- `GET /comments?post_id={id}` - Get comments for post
- `POST /comments` - Create comment (requires auth)
- `PUT /comments/{comment_id}` - Update comment (requires auth, owner only)
- `DELETE /comments/{comment_id}` - Soft delete comment (requires auth, owner only)
- `GET /comments/{comment_id}/replies` - Get comment replies

#### Like Service
- `GET /likes/count?post_id={id}` - Get like count for post
- `GET /likes/status?post_id={id}` - Check if user liked post (requires auth)
- `POST /likes` - Like a post (requires auth)
- `DELETE /likes/{post_id}` - Unlike a post (requires auth)

## Database Schema

PostgreSQL with separate schemas for each service:

- `auth.users` - User credentials
- `auth.refresh_tokens` - Refresh token storage
- `users.profiles` - User profiles
- `posts.posts` - Blog posts
- `posts.tags` - Post tags
- `posts.post_tags` - Many-to-many relationship
- `comments.comments` - Comments with nested replies
- `likes.likes` - Post likes

## AWS Deployment

### Prerequisites

- AWS Account
- Terraform >= 1.0
- AWS CLI configured

### Deploy Infrastructure

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan \
  -var="db_password=your_secure_password" \
  -var="jwt_secret_key=your_jwt_secret_key"

# Apply deployment
terraform apply \
  -var="db_password=your_secure_password" \
  -var="jwt_secret_key=your_jwt_secret_key"
```

### Push Docker Images to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push each service
docker build -t blogin-auth-service services/auth-service
docker tag blogin-auth-service:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/blogin-auth-service:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/blogin-auth-service:latest

# Repeat for other services...
```

### CI/CD with GitHub Actions

The repository includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that:

1. Runs linters and tests
2. Builds Docker images
3. Pushes images to ECR
4. Updates ECS services

Configure these secrets in your GitHub repository:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ACCOUNT_ID`

## Development

### Project Structure

```
blogin/
├── services/
│   ├── auth-service/         # Authentication microservice
│   ├── user-service/          # User management microservice
│   ├── post-service/          # Blog post microservice
│   ├── comment-service/       # Comment microservice
│   ├── like-service/          # Like microservice
│   ├── gateway/               # Nginx reverse proxy
│   └── frontend/              # Vue.js frontend
├── infrastructure/
│   └── terraform/             # Terraform IaC
├── scripts/
│   └── init-db.sh            # Database initialization
├── docker-compose.yml        # Local development orchestration
├── Makefile                  # Convenience commands
└── README.md                 # This file
```

### Running Tests

```bash
# Run tests for all services
make test

# Run tests for specific service
cd services/auth-service
pytest
```

### Code Linting

```bash
# Run linters for all services
make lint
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Access token expiry
- `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token expiry
- `AWS_REGION` - AWS region for deployment

## Frontend Features

- JWT-based authentication with automatic token refresh
- Post feed with infinite scroll pagination
- Markdown rendering for post content
- Nested comment system with replies
- Like/unlike functionality
- User profile management
- Responsive design
- Route guards for protected routes

## Security

- JWT tokens with refresh token rotation
- Password hashing with bcrypt
- CORS configured for API access
- Security groups restricting access in AWS
- Secrets stored in AWS Parameter Store
- Input validation on all endpoints

## Monitoring

- CloudWatch Logs for all services
- CloudWatch Dashboard for metrics
- Health check endpoints on all services
- CloudWatch Alarms for critical metrics

## Cost Optimization

For learning and development:

- Use AWS Free Tier (t3.micro, RDS db.t3.micro)
- Single NAT Gateway for dev
- No Multi-AZ for development
- Use Fargate Spot for non-critical tasks
- Scheduled scaling to stop dev environments

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps

# View PostgreSQL logs
docker-compose logs postgres

# Connect to PostgreSQL
make psql
```

### Service Not Starting

```bash
# View service logs
docker-compose logs <service-name>

# Restart specific service
docker-compose restart <service-name>
```

### Token Issues

If you get 401 errors, the token may have expired:
- The frontend automatically refreshes tokens
- Or logout and login again

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## License

MIT License - feel free to use this for learning and building your own projects!

## Support

For issues or questions:
- Open an issue on GitHub
- Check the logs: `make logs`
- Review API docs at `/docs` on any service

## Roadmap

Future enhancements:
- [ ] Add SQS/SNS for async processing
- [ ] Implement Redis caching
- [ ] Add image upload to S3
- [ ] Email notifications service
- [ ] Full-text search with Elasticsearch
- [ ] Real-time updates with WebSockets
- [ ] Mobile app
- [ ] OAuth2 social login
