# Production

## Setup server
- Edit `infra/inventory.ini`: `91.107.225.178 ansible_user=root ansible_python_interpreter=/usr/bin/python3`
- Run: `ansible-playbook -i inventory.ini bootstrap.yml`
- Revert changes in `infra/inventory.ini`

## Setup app
`ansible-playbook -i inventory.ini setup.yml`