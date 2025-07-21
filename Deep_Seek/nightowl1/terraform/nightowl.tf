# Terraform configuration for NightOwl deployment
provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "nightowl_scanner" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.medium"
  
  tags = {
    Name = "NightOwl-Recon-Scanner"
  }
  
  user_data = <<-EOF
              #!/bin/bash
              git clone https://github.com/n00bhack3r/nightowl.git
              cd nightowl
              pip install -r requirements.txt
              EOF
}