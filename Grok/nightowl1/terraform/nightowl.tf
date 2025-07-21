provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_image" "nightowl" {
  name = "nightowl:latest"
}

resource "docker_container" "nightowl" {
  image = docker_image.nightowl.image_id
  name  = "nightowl"
  env = [
    "OPENAI_API_KEY=${var.openai_api_key}"
  ]
  volumes {
    host_path      = "${path.cwd}/output"
    container_path = "/app/output"
  }
}