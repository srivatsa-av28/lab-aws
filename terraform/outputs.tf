output "instance_ids" {
  description = "IDs of created instances"
  value       = aws_instance.managed_instance[*].id
}

output "instance_public_ips" {
  description = "Public IPs of created instances"
  value       = aws_instance.managed_instance[*].public_ip
}

output "instance_private_ips" {
  description = "Private IPs of created instances"
  value       = aws_instance.managed_instance[*].private_ip
}