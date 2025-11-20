# Database Migration Lab: SQL Server/Oracle to PostgreSQL

## 🎯 Lab Overview

This is a **hands-on, local database migration lab** that simulates a complete enterprise migration from SQL Server/Oracle to PostgreSQL using Docker, GitHub Actions, and open-source tools—**no AWS account required**.

### What You'll Learn

- ✅ Set up multi-database environments locally using Docker Compose
- ✅ Convert schemas using AWS SCT and manual remediation
- ✅ Build data migration pipelines with Python and Debezium CDC
- ✅ Automate testing and validation with GitHub Actions
- ✅ Implement DevOps best practices for database migrations
- ✅ Perform simulated cutover with rollback procedures

### Technologies Used

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Source DBs** | SQL Server 2022, Oracle 21c XE | Source databases to migrate from |
| **Target DB** | PostgreSQL 16 | Target database |
| **CDC** | Debezium + Kafka | Change Data Capture for continuous replication |
| **Orchestration** | Docker Compose | Local environment management |
| **CI/CD** | GitHub Actions | Automated testing and deployment |
| **Validation** | Python (pandas, psycopg2) | Data validation and reconciliation |
| **Schema Conversion** | AWS SCT (local) | Schema assessment and conversion |
| **Optional Cloud Simulation** | LocalStack | Simulate AWS services locally |

---

## 📋 Prerequisites

### Required Software

1. **Docker Desktop** (Windows 11)
   - Download: https://www.docker.com/products/docker-desktop
   - Minimum: 8GB RAM allocated, 50GB disk space

2. **Git & GitHub Account**
   - Download Git: https://git-scm.com/downloads
   - Create free GitHub account: https://github.com

3. **Python 3.10+**
   - Download: https://www.python.org/downloads/
   - Add to PATH during installation

4. **AWS Schema Conversion Tool (SCT)** - optional
   - Download: https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Installing.html
   - Runs locally without AWS account

5. **VS Code** (recommended)
   - Download: https://code.visualstudio.com/
   - Extensions: Docker, Python, SQL

### System Requirements

- **OS**: Windows 11 Pro (your current setup)
- **RAM**: 16GB minimum (you have this)
- **CPU**: 4+ cores
- **Disk**: 50GB free space

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/db-migration-lab.git
cd db-migration-lab
```

### 2. Create Python Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Start All Services

```bash
docker-compose up -d
```

This will start:
- SQL Server 2022 (port 1433)
- Oracle 21c XE (port 1521)
- PostgreSQL 16 (port 5432)
- Kafka + Zookeeper (for CDC)
- Debezium Connect (for change capture)
- LocalStack (optional AWS simulation)

### 4. Verify Services

```bash
python migration/python/connectivity_check.py
```

Expected output:
```
✅ SQL Server: Connected successfully
✅ Oracle: Connected successfully  
✅ PostgreSQL: Connected successfully
✅ Kafka: Connected successfully
```

### 5. Run Your First Migration

```bash
# Load sample data into source databases
docker-compose exec sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P YourPassword123 -i /init/seed-data.sql

# Run schema migration
python migration/python/run_migrations.py --env local --phase schema

# Run data migration (full load)
python migration/python/run_migrations.py --env local --phase data

# Validate migration
python migration/python/rowcount_validate.py --env local
```

---

## 📚 Lab Modules

### Module 1: Environment Setup (30 mins)
- Install prerequisites
- Start Docker containers
- Verify connectivity
- Load sample data

**👉 [Start Module 1](docs/01-setup.md)**

---

### Module 2: Schema Conversion (45 mins)
- Run AWS SCT assessment
- Generate PostgreSQL DDL
- Manual conversion exercises
- Version control schema changes

**👉 [Start Module 2](docs/02-schema-conversion.md)**

---

### Module 3: Data Migration (60 mins)
- Bulk data migration with Python
- Set up Debezium for CDC
- Configure Kafka connectors
- Monitor replication lag

**👉 [Start Module 3](docs/03-data-migration.md)**

---

### Module 4: Testing & Validation (45 mins)
- Row count validation
- Financial reconciliation
- Data quality checks
- Performance comparison

**👉 [Start Module 4](docs/04-testing.md)**

---

### Module 5: CI/CD Pipeline (60 mins)
- GitHub Actions workflows
- Environment-specific configs
- Automated testing
- Deployment automation

**👉 [Start Module 5](docs/05-cicd-pipeline.md)**

---

### Module 6: Cutover Simulation (45 mins)
- Pre-cutover checklist
- Freeze writes on source
- Final CDC sync
- Application switchover
- Rollback procedures

**👉 [Start Module 6](docs/06-cutover.md)**

---

## 🗂️ Repository Structure

```
db-migration-lab/
├── README.md                          # This file
├── docker-compose.yml                 # All database containers
├── requirements.txt                   # Python dependencies
├── .github/workflows/                 # CI/CD pipelines
│   ├── dev-migration.yml
│   ├── qa-migration.yml
│   └── validate-migration.yml
├── databases/                         # Database initialization
│   ├── sqlserver/
│   │   ├── Dockerfile
│   │   ├── init.sql
│   │   └── seed-data.sql
│   ├── oracle/
│   │   ├── Dockerfile
│   │   ├── init.sql
│   │   └── seed-data.sql
│   └── postgresql/
│       ├── init.sql
│       └── extensions.sql
├── migration/
│   ├── sct-output/                   # SCT-generated DDL
│   ├── manual-fixes/                 # Manual conversions
│   └── python/
│       ├── connectivity_check.py
│       ├── rowcount_validate.py
│       ├── finance_reconcile.py
│       └── run_migrations.py
├── envs/                             # Environment configs
│   ├── local.yaml
│   ├── dev.yaml
│   └── qa.yaml
├── tests/                            # Automated tests
│   ├── test_schema.py
│   ├── test_data.py
│   └── test_performance.py
└── docs/                             # Lab modules
    ├── 01-setup.md
    ├── 02-schema-conversion.md
    ├── 03-data-migration.md
    ├── 04-testing.md
    ├── 05-cicd-pipeline.md
    └── 06-cutover.md
```

---

## 🎓 Learning Path

### Beginner Track (First time with migrations)
1. Complete Modules 1-4 sequentially
2. Skip advanced CDC initially
3. Focus on schema conversion and validation
4. Estimated time: 4-5 hours

### Intermediate Track (Some DB experience)
1. Complete all modules
2. Implement CDC with Debezium
3. Set up GitHub Actions pipelines
4. Estimated time: 6-8 hours

### Advanced Track (Migration professional)
1. Complete all modules
2. Customize for your specific use case
3. Add additional validation logic
4. Integrate with your real environment
5. Estimated time: 8-10 hours

---

## 🔧 Troubleshooting

### Docker Issues

**Problem**: Containers fail to start
```bash
# Check Docker resources
docker system df
docker system prune -a  # Clean up if needed

# Check logs
docker-compose logs sqlserver
docker-compose logs postgresql
```

**Problem**: Port conflicts
```bash
# Check what's using ports
netstat -ano | findstr "1433"  # SQL Server
netstat -ano | findstr "5432"  # PostgreSQL

# Edit docker-compose.yml to use different ports if needed
```

### Database Connection Issues

**Problem**: Can't connect to SQL Server
```bash
# Verify container is running
docker ps | findstr sqlserver

# Check logs
docker-compose logs sqlserver

# Try manual connection
docker exec -it db-migration-lab-sqlserver-1 /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P YourPassword123
```

### Python Issues

**Problem**: Module not found
```bash
# Ensure virtual environment is activated
.\venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📖 Additional Resources

### Documentation
- [AWS SCT User Guide](https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/)
- [Debezium Documentation](https://debezium.io/documentation/)
- [PostgreSQL Migration Guide](https://www.postgresql.org/docs/current/migration.html)

### Sample Data
- Databases use simplified AdventureWorks-style schema
- Includes: Customers, Orders, Products, Transactions
- Pre-loaded with ~10K rows for testing

### Interview Prep
- Each module includes "Interview Questions" section
- Key talking points highlighted
- Common gotchas explained

---

## 🤝 Contributing & Feedback

This is a learning lab—feel free to:
- Extend with additional databases (MySQL, MongoDB)
- Add more complex migration scenarios
- Improve Python scripts
- Share your experience

---

## 📝 License

This lab is for educational purposes. Sample data and scripts are provided as-is for learning.

---

## 🚦 Next Steps

**Ready to start?**

👉 **[Begin with Module 1: Environment Setup](docs/01-setup.md)**

---

**Questions or issues?** Create an issue in this repository or refer to the troubleshooting section above.

**Good luck with your migration journey!** 🚀
