def mask_email(email: str) -> str:
    """
    Mascara um endereço de email para logs seguros

    Examples:
        user@example.com -> u***@e******.com
        test.user@gmail.com -> t***.u***@g****.com
        a@b.co -> a@b.co (emails muito curtos não são mascarados)

    Args:
        email: Endereço de email a ser mascarado

    Returns:
        Email mascarado
    """
    if not email or "@" not in email:
        return email

    try:
        local, domain = email.split("@", 1)

        # Para partes muito pequenas, não mascara
        if len(local) <= 2:
            masked_local = local
        else:
            # Mascara meio da parte local
            if "." in local:
                # Se tem ponto, mascara cada parte separadamente
                parts = local.split(".")
                masked_parts = []
                for part in parts:
                    if len(part) <= 2:
                        masked_parts.append(part)
                    else:
                        masked_parts.append(part[0] + "*" * (len(part) - 1))
                masked_local = ".".join(masked_parts)
            else:
                masked_local = local[0] + "*" * (len(local) - 1)

        # Mascara domínio
        if "." in domain:
            domain_parts = domain.split(".")
            domain_name = domain_parts[0]
            domain_tld = ".".join(domain_parts[1:])

            if len(domain_name) <= 2:
                masked_domain = f"{domain_name}.{domain_tld}"
            else:
                masked_domain = (
                    f"{domain_name[0]}{'*' * (len(domain_name) - 1)}.{domain_tld}"
                )
        else:
            masked_domain = domain

        return f"{masked_local}@{masked_domain}"

    except Exception:
        # Em caso de erro, retorna email parcialmente mascarado
        return f"***@{email.split('@')[-1]}" if "@" in email else "***"
