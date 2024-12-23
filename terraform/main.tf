terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  backend "s3" {
    bucket         = "tf-remote-state-cac44df4-a679-48e0-bebc-e38b3de84b72"
    key            = "tf-state"
    region         = "us-east-1"
    dynamodb_table = "tf-remote-state"
    encrypt = true
  }

}

provider "aws" {
  profile = "default"
  region  = "us-east-1"
}

resource "aws_s3_bucket" "tf_state_bucket" {
  bucket = "tf-remote-state-cac44df4-a679-48e0-bebc-e38b3de84b72"
}

resource "aws_dynamodb_table" "tf_state_dynamodb_table" {
    name = "tf-remote-state"
    hash_key = "LockID"
    read_capacity = 20
    write_capacity = 20

    attribute {
        name = "LockID"
        type = "S"
    }
}