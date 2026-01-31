<script setup>
</script>

<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-brand">
          <span class="footer-logo">📝 Blogin</span>
          <p class="footer-tagline">Share your stories with the world</p>
        </div>
        
        <div class="footer-links">
          <a href="#" class="footer-link">About</a>
          <a href="#" class="footer-link">Terms</a>
          <a href="#" class="footer-link">Privacy</a>
          <a href="#" class="footer-link">Contact</a>
        </div>
      </div>
      
      <div class="footer-bottom">
        <p>&copy; {{ new Date().getFullYear() }} Blogin. Built with Vue 3 & Microservices.</p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background-color: var(--bg-color);
  border-top: 1px solid var(--border-color);
  padding: 2rem 0 1rem;
  margin-top: auto;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.footer-brand {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.footer-logo {
  font-weight: 700;
  font-size: 1.125rem;
  color: var(--text-color);
}

.footer-tagline {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.footer-links {
  display: flex;
  gap: 1.5rem;
}

.footer-link {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.2s;
}

.footer-link:hover {
  color: var(--primary-color);
}

.footer-bottom {
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  text-align: center;
}

.footer-bottom p {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

@media (max-width: 640px) {
  .footer-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .footer-links {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
