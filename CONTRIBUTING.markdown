# Contributing to Unisights

Thank you for your interest in contributing to Unisights, the open-source, privacy-first real-time analytics platform! 🎉 We welcome contributions from the community to make Unisights better, whether you're fixing bugs, adding features, improving documentation, or sharing ideas. This guide outlines how you can get involved.

## 📌 Getting Started

1. **Explore the Project**: Check out the [README.md](README.md) to understand Unisights’ architecture, tech stack (WASM SDK, FastAPI, Kafka, Druid, Superset), and setup instructions.
2. **Join the Community**: Visit our GitHub Discussions or Issues page to connect, ask questions, or propose ideas.
3. **Find an Issue**: Look for issues labeled `good first issue` for beginners or `help wanted` for more complex tasks.

## 🚀 How to Contribute

### Step 1: Fork and Clone

1. Fork the repository to your GitHub account.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/unisights.git
   cd unisights
   ```

### Step 2: Set Up Development

- **Prerequisites**: Ensure you have Docker, Docker Compose, Rust (for SDK), and Python 3.10+ (for ingestion service) installed. See [README.md](README.md) for details.
- **SDK Development**:
  ```bash
  cd client-sdk
  npm install
  npm run build
  ```
- **Ingestion Service**:
  ```bash
  cd ingestion-service
  pip install -r requirements.txt
  uvicorn main:app --reload
  ```
- **Test the Stack**: Run `docker-compose up -d` to spin up Kafka, Druid, Superset, and other services.

### Step 3: Make Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/my-feature
   ```
2. Follow coding guidelines:
   - Use clear, descriptive commit messages (e.g., `feat: add geo-filter to Superset dashboard`).
   - Keep code style consistent (e.g., PEP 8 for Python, Prettier for TypeScript).
   - Write tests where applicable (e.g., unit tests for FastAPI endpoints).
3. Update documentation if you modify or add features.

### Step 4: Submit a Pull Request

1. Push your branch:
   ```bash
   git push origin feature/my-feature
   ```
2. Open a Pull Request (PR) on GitHub, describing:
   - What you changed and why.
   - Any issues your PR addresses (e.g., `Fixes #123`).
   - Testing steps or screenshots (e.g., for dashboard changes).
3. Ensure your PR passes CI checks (if set up).

### Step 5: Code Review

- Expect feedback from maintainers or community members.
- Be responsive to comments and make requested changes.
- Once approved, your PR will be merged!

## 💡 Contribution Ideas

- **Features**: Add new event types, enhance WASM SDK performance, or integrate ML models for analytics.
- **Bug Fixes**: Address issues in the Issues tab (e.g., Kafka connection errors, Superset query bugs).
- **Docs**: Improve setup guides, add tutorials (e.g., for e-commerce tracking), or translate docs.
- **Dashboards**: Create sample Superset dashboards for common use cases (e.g., funnels, retention).
- **Tests**: Add unit or integration tests for the FastAPI service or WASM SDK.

## 📜 Guidelines

- **Respect the Code of Conduct**: See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for a welcoming, inclusive community.
- **Keep PRs Focused**: Small, specific changes are easier to review than large, mixed updates.
- **Test Locally**: Ensure your changes work with `docker-compose up` or local services.
- **Ask for Help**: If stuck, post in Discussions or comment on an issue.

## 🌟 Why Contribute?

By contributing, you’re helping build a privacy-first, scalable analytics platform that empowers developers and businesses. Plus, you’ll gain experience with cutting-edge tools like WASM, Kafka, and Druid, and become part of a growing open-source community!

If you have questions, reach out via GitHub Issues or Discussions. We can’t wait to see your contributions! 🚀
