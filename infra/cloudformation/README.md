# CloudFormation Templates

## rds-s3-lab.yaml

A lab-grade CloudFormation template that deploys:
- **RDS PostgreSQL** instance (free-tier optimized: db.t4g.micro, gp2 storage, no backups)
- **S3 bucket** with encryption and public access blocking
- **DB subnet group** for multi-AZ deployment
- **EC2 security group** for PostgreSQL access

### Key Features

- **Parameterized**: VPC ID, subnet IDs, DB username/password, instance class, and environment tag are configurable.
- **Optional SG Attachment**: Security groups can be attached at deploy time or post-deploy using the AWS CLI.
- **Free Tier Friendly**: Configured for minimal costs (db.t4g.micro, gp2, BackupRetentionPeriod=0).

### Deployment Modes

#### Mode 1: Workaround (Recommended for new accounts with EarlyValidation hooks)

Deploy the RDS instance without attaching security groups in CloudFormation, then attach them post-deploy via CLI.

```powershell
# Step 1: Deploy the stack (no SGs attached)
aws cloudformation deploy `
  --region ap-south-1 `
  --stack-name db-migration-lab-stack `
  --template-file infra/cloudformation/rds-s3-lab.yaml `
  --parameter-overrides `
    VpcId=vpc-01234567 `
    DBSubnetIds="subnet-aaa,subnet-bbb" `
    DBUsername=labuser `
    DBPassword='YourStrongPassword!' `
    Environment=lab `
    AttachSecurityGroup=false

# Step 2: Get the RDS instance identifier and attach security groups
$DBInstanceId = (aws rds describe-db-instances --region ap-south-1 --query "DBInstances[0].DBInstanceIdentifier" --output text)
aws rds modify-db-instance --region ap-south-1 `
  --db-instance-identifier $DBInstanceId `
  --vpc-security-group-ids sg-0123abcd sg-0456efgh `
  --apply-immediately
```

**When to use**: Your AWS account is new or has EarlyValidation hooks that block VpcSecurityGroupIds in change-sets.

#### Mode 2: Single-step (Standard accounts)

Deploy the stack with security groups attached in one change-set (if your account permits it).

```powershell
aws cloudformation deploy `
  --region ap-south-1 `
  --stack-name db-migration-lab-stack `
  --template-file infra/cloudformation/rds-s3-lab.yaml `
  --parameter-overrides `
    VpcId=vpc-01234567 `
    DBSubnetIds="subnet-aaa,subnet-bbb" `
    DBUsername=labuser `
    DBPassword='YourStrongPassword!' `
    AttachSecurityGroup=true `
    SecurityGroupIds="sg-0123abcd,sg-0456efgh" `
    Environment=lab
```

**When to use**: Your account allows VpcSecurityGroupIds in RDS instances during change-set creation (standard accounts).

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `VpcId` | String | — | VPC ID where resources will be deployed |
| `DBSubnetIds` | CommaDelimitedList | — | List of at least 2 subnet IDs for the DB subnet group |
| `DBUsername` | String | — | Master username for RDS database (8–128 chars) |
| `DBPassword` | String | — | Master password for RDS database (8–128 chars) |
| `DBInstanceClass` | String | `db.t4g.micro` | RDS instance type (free tier: db.t4g.micro) |
| `Environment` | String | `lab` | Environment name for tagging (dev, lab, staging, prod) |
| `AttachSecurityGroup` | String | `false` | Set to `true` to attach SGs in the change-set; `false` for post-deploy attachment |
| `SecurityGroupIds` | CommaDelimitedList | — | Comma-separated list of existing SG IDs (only used if AttachSecurityGroup=true) |

### Outputs

After deployment, CloudFormation exports these stack outputs:

- **RDSEndpoint**: PostgreSQL RDS endpoint address (e.g., `db-*.c1ymosa0m28v.ap-south-1.rds.amazonaws.com`)
- **RDSPort**: PostgreSQL port (default: 5432)
- **BucketName**: S3 bucket name
- **BucketArn**: S3 bucket ARN
- **DBInstanceIdentifier**: RDS database instance identifier
- **DBSubnetGroupName**: DB subnet group name
- **SecurityGroupId**: In-template security group ID

### Troubleshooting

#### EarlyValidation::PropertyValidation Error

**Error**: `AWS::EarlyValidation::PropertyValidation` when creating a change-set with `VpcSecurityGroupIds`.

**Solution**: Use Mode 1 (workaround). Set `AttachSecurityGroup=false` and attach SGs post-deploy via `aws rds modify-db-instance --vpc-security-group-ids ...`.

**Root cause**: Your account may have organization-level guardrails or an EarlyValidation hook preventing RDS VpcSecurityGroupIds in change-sets. This is common in newly created AWS accounts.

#### Engine Version Not Available

**Error**: `Cannot find version X.Y for postgres`.

**Solution**: Check available versions for your region:
```powershell
aws rds describe-db-engine-versions --region ap-south-1 --engine postgres --query 'DBEngineVersions[*].EngineVersion'
```

Edit the template `EngineVersion` to a supported version.

#### RDS Instance Takes 5+ Minutes to Create

This is normal. RDS provisioning typically takes 5–10 minutes. You can monitor progress:

```powershell
aws rds describe-db-instances --region ap-south-1 --db-instance-identifier <DBInstanceId> --query 'DBInstances[0].DBInstanceStatus'
```

### Cost Estimate (Free Tier)

- **RDS db.t4g.micro**: ~$0/mo (eligible for 750 hours/month free tier; ~31 days = 744 hours)
- **S3 storage**: ~$0/mo (5 GB free tier; adjust versioning if needed)
- **Data transfer**: ~$0/mo (1 GB/month free tier egress)

**Total**: Approximately $0/mo if within free tier limits.

### Clean Up

To avoid unexpected charges, delete the stack when no longer needed:

```powershell
aws cloudformation delete-stack --region ap-south-1 --stack-name db-migration-lab-stack
aws cloudformation wait stack-delete-complete --region ap-south-1 --stack-name db-migration-lab-stack
```

### Related Templates

- **rds-s3-lab-workaround.yaml**: Minimal workaround template (no VpcSecurityGroupIds). Use as a reference or fallback if the conditional in rds-s3-lab.yaml causes issues.
