---
version: "1.0"
type: SPACE
---

# Web Development

This space covers modern web development patterns, conventions, and best practices.

## Frontend Technologies

### HTML5 & Semantic Markup
- Use semantic elements (`<header>`, `<nav>`, `<main>`, `<article>`)
- Ensure accessibility with ARIA labels
- Structure documents logically

### CSS Best Practices
- Use CSS Grid and Flexbox for layouts
- Prefer CSS variables for theming
- Follow BEM or similar naming convention
- Mobile-first responsive design

### JavaScript/TypeScript
- ES6+ modern syntax
- Async/await for asynchronous operations
- Type safety with TypeScript
- Modular code organization

## Backend Patterns

### RESTful APIs
- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Return appropriate status codes
- Version your APIs (`/api/v1/`)
- Document with OpenAPI/Swagger

### Authentication
- Use JWT or OAuth2 for stateless auth
- Implement proper password hashing (bcrypt, argon2)
- HTTPS only in production
- Rate limiting to prevent abuse

## Database Design

- Normalize where appropriate, denormalize for performance
- Use migrations for schema changes
- Index frequently queried columns
- Implement proper backup strategies

## Testing Strategy

- Unit tests for business logic
- Integration tests for API endpoints
- End-to-end tests for critical user flows
- Aim for >80% code coverage

## DevOps

- CI/CD pipelines for automated deployment
- Container-based deployments (Docker)
- Environment-specific configurations
- Monitoring and logging

## Security Considerations

- Input validation and sanitization
- Protection against SQL injection, XSS, CSRF
- Secure headers (CSP, HSTS)
- Regular dependency updates

## Performance

- Lazy loading for large resources
- Image optimization and CDN usage
- Caching strategies (browser, CDN, server)
- Code splitting and tree shaking

---

**Related Prompts**: `GUIDE-*-Web-Security`, `PROMPT-*-API-Design`
