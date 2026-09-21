from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import connection, transaction
from django.utils import timezone

from apps.usuarios.models import PerfilUsuario
from apps.operaciones.models import Material, LoteMaterial, EstudioPrevio, Maquina, Proceso, RegistroMerma
from apps.auditoria.utils import registrar_log

class Command(BaseCommand):
    help = 'Puebla la base de datos con roles, usuarios y datos iniciales de prueba para verificar la conexión (Criterio 2.1.1)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE(">>> 1. Verificando conexión a la Base de Datos..."))
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                resultado = cursor.fetchone()
            self.stdout.write(self.style.SUCCESS(f"    [OK] Conexión establecida con éxito (motor: {connection.vendor})."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"    [ERROR] Fallo en la conexión a la base de datos: {e}"))
            return

        with transaction.atomic():
            self.stdout.write(self.style.NOTICE(">>> 2. Creando Grupos de Seguridad RBAC..."))
            grupos = ['Operador', 'Supervisor', 'Encargado']
            for g_name in grupos:
                group, created = Group.objects.get_or_create(name=g_name)
                if created:
                    self.stdout.write(f"    - Grupo creado: {g_name}")

            self.stdout.write(self.style.NOTICE(">>> 3. Creando Usuarios y Perfiles de Prueba..."))
            usuarios_data = [
                {
                    'username': 'operador1',
                    'first_name': 'Carlos',
                    'last_name': 'Gómez',
                    'email': 'carlos.operador@fundicion.local',
                    'rol': 'OPERADOR',
                    'is_staff': False,
                    'is_superuser': False,
                    'password': 'Operador2026!'
                },
                {
                    'username': 'supervisor1',
                    'first_name': 'Marcela',
                    'last_name': 'Rojas',
                    'email': 'marcela.supervisor@fundicion.local',
                    'rol': 'SUPERVISOR',
                    'is_staff': False,
                    'is_superuser': False,
                    'password': 'Supervisor2026!'
                },
                {
                    'username': 'encargado1',
                    'first_name': 'Roberto',
                    'last_name': 'Silva',
                    'email': 'roberto.encargado@fundicion.local',
                    'rol': 'ENCARGADO',
                    'is_staff': True,
                    'is_superuser': False,
                    'password': 'Encargado2026!'
                },
                {
                    'username': 'admin',
                    'first_name': 'Administrador',
                    'last_name': 'Principal',
                    'email': 'admin@fundicion.local',
                    'rol': 'ENCARGADO',
                    'is_staff': True,
                    'is_superuser': True,
                    'password': 'Admin2026!'
                },
            ]

            usuarios_creados = {}
            for u in usuarios_data:
                user, created = User.objects.get_or_create(
                    username=u['username'],
                    defaults={
                        'first_name': u['first_name'],
                        'last_name': u['last_name'],
                        'email': u['email'],
                        'is_staff': u['is_staff'],
                        'is_superuser': u['is_superuser'],
                    }
                )
                user.set_password(u['password'])
                user.save()
                
                perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
                perfil.rol = u['rol']
                perfil.save()

                # Asignar a grupo
                if u['rol'] == 'OPERADOR':
                    user.groups.add(Group.objects.get(name='Operador'))
                elif u['rol'] == 'SUPERVISOR':
                    user.groups.add(Group.objects.get(name='Supervisor'))
                elif u['rol'] == 'ENCARGADO':
                    user.groups.add(Group.objects.get(name='Encargado'))

                usuarios_creados[u['username']] = user
                self.stdout.write(f"    - Usuario listo: {u['username']} (Rol: {u['rol']}, Contraseña: {u['password']})")

            self.stdout.write(self.style.NOTICE(">>> 4. Creando Catálogo de Materiales y Aleaciones..."))
            mat_al, _ = Material.objects.get_or_create(
                codigo='AL-A380',
                defaults={'nombre': 'Aluminio A380 Fundición', 'densidad_g_cm3': Decimal('2.71'), 'punto_fusion_c': 595, 'descripcion': 'Aleación de aluminio para inyección y vaciado.'}
            )
            mat_br, _ = Material.objects.get_or_create(
                codigo='BR-FOS',
                defaults={'nombre': 'Bronce Fosforado UNS C54400', 'densidad_g_cm3': Decimal('8.89'), 'punto_fusion_c': 1000, 'descripcion': 'Bronce de alta resistencia al desgaste.'}
            )
            mat_fe, _ = Material.objects.get_or_create(
                codigo='FE-NOD',
                defaults={'nombre': 'Hierro Nodular Dúctil ASTM A536', 'densidad_g_cm3': Decimal('7.10'), 'punto_fusion_c': 1150, 'descripcion': 'Hierro fundido con grafito esferoidal.'}
            )

            self.stdout.write(self.style.NOTICE(">>> 5. Creando Catálogo de Maquinarias y Procesos..."))
            maq1, _ = Maquina.objects.get_or_create(codigo='HORN-IND-01', defaults={'nombre': 'Horno de Inducción Inductotherm 500kg', 'tipo': 'Horno de Fusión', 'capacidad_max_kg': Decimal('500.00')})
            maq2, _ = Maquina.objects.get_or_create(codigo='TORN-CNC-02', defaults={'nombre': 'Torno CNC Haas ST-20', 'tipo': 'Mecanizado', 'capacidad_max_kg': Decimal('200.00')})
            maq3, _ = Maquina.objects.get_or_create(codigo='PRENS-INY-01', defaults={'nombre': 'Inyectora de Cámara Fría 400T', 'tipo': 'Vaciado a Presión', 'capacidad_max_kg': Decimal('350.00')})

            proc_fus, _ = Proceso.objects.get_or_create(codigo='PROC-FUS', defaults={'nombre': 'Fusión y Escoriado en Horno', 'temperatura_operacion_c': 720})
            proc_col, _ = Proceso.objects.get_or_create(codigo='PROC-COL', defaults={'nombre': 'Vaciado y Colada en Molde', 'temperatura_operacion_c': 680})
            proc_reb, _ = Proceso.objects.get_or_create(codigo='PROC-REB', defaults={'nombre': 'Corte de Mazarotas y Rebabado'})
            proc_maq, _ = Proceso.objects.get_or_create(codigo='PROC-MAQ', defaults={'nombre': 'Mecanizado y Acabado CNC'})

            self.stdout.write(self.style.NOTICE(">>> 6. Creando Lotes de Prueba y Validando Flujo Gatekeeper (M1, M4, M5)..."))
            # Lote 1: Con Estudio Previo Aprobado y Mermas registradas
            lote1, _ = LoteMaterial.objects.get_or_create(
                codigo_lote='LOT-2026-AL-001',
                defaults={
                    'material': mat_al,
                    'peso_inicial_kg': Decimal('1000.00'),
                    'proveedor': 'Metales del Sur S.A.',
                    'observaciones': 'Lote certificado para producción de piezas automotrices.'
                }
            )
            estudio1, _ = EstudioPrevio.objects.get_or_create(
                lote=lote1,
                defaults={
                    'peso_calibrado_kg': Decimal('1000.00'),
                    'porcentaje_pureza': Decimal('99.20'),
                    'porcentaje_humedad': Decimal('0.30'),
                    'tolerancia_merma_max_pct': Decimal('7.50'),
                    'estado': 'APROBADO',
                    'responsable_estudio': usuarios_creados['operador1'],
                    'supervisor_aprobador': usuarios_creados['supervisor1'],
                    'fecha_aprobacion': timezone.now(),
                    'observaciones_metrologicas': 'Báscula Toledo M-500 calibrada el 15/09/2026. Lote apto para colada.'
                }
            )

            # Mermas registradas para Lote 1
            if not lote1.mermas.exists():
                m1 = RegistroMerma.objects.create(
                    lote=lote1,
                    proceso=proc_fus,
                    maquina=maq1,
                    peso_merma_kg=Decimal('42.50'),
                    tipo_merma='ESCORIA',
                    operador=usuarios_creados['operador1'],
                    observaciones='Escoria superficial retirada en primera fusión.'
                )
                m2 = RegistroMerma.objects.create(
                    lote=lote1,
                    proceso=proc_maq,
                    maquina=maq2,
                    peso_merma_kg=Decimal('18.30'),
                    tipo_merma='VIRUTA',
                    operador=usuarios_creados['operador1'],
                    observaciones='Viruta recolectada de mecanizado CNC de acabado.'
                )

            # Lote 2: Con Estudio Previo en Revisión (para probar bloqueo de Gatekeeper M5)
            lote2, _ = LoteMaterial.objects.get_or_create(
                codigo_lote='LOT-2026-BR-002',
                defaults={
                    'material': mat_br,
                    'peso_inicial_kg': Decimal('500.00'),
                    'proveedor': 'Aleaciones Industriales Ltda.',
                    'observaciones': 'Lote de bronce para bujes y cojinetes.'
                }
            )
            estudio2, _ = EstudioPrevio.objects.get_or_create(
                lote=lote2,
                defaults={
                    'peso_calibrado_kg': Decimal('498.80'),
                    'porcentaje_pureza': Decimal('98.70'),
                    'porcentaje_humedad': Decimal('0.60'),
                    'tolerancia_merma_max_pct': Decimal('5.00'),
                    'estado': 'EN_REVISION',
                    'responsable_estudio': usuarios_creados['operador1'],
                    'observaciones_metrologicas': 'Pesaje preliminar. Pendiente revisión de supervisor.'
                }
            )

            # Lote 3: Sin Estudio Previo (para probar inicio de flujo)
            lote3, _ = LoteMaterial.objects.get_or_create(
                codigo_lote='LOT-2026-FE-003',
                defaults={
                    'material': mat_fe,
                    'peso_inicial_kg': Decimal('2000.00'),
                    'proveedor': 'Fundición Central S.A.',
                    'observaciones': 'Hierro nodular recién ingresado a bodega.'
                }
            )

            # Registro de Log Inicial
            registrar_log(
                accion='CREATE',
                tabla_afectada='sistema_inicializacion',
                registro_id=None,
                detalles="Inicialización exitosa de base de datos con datos de prueba y roles RBAC.",
                usuario=usuarios_creados['admin'],
                ip_origen='127.0.0.1'
            )

        self.stdout.write(self.style.SUCCESS(">>> [LISTO] Base de datos poblada y verificada exitosamente."))
        self.stdout.write(self.style.SUCCESS("    Credenciales de acceso:"))
        self.stdout.write("    * Operador:   usuario: operador1   | clave: Operador2026!")
        self.stdout.write("    * Supervisor: usuario: supervisor1 | clave: Supervisor2026!")
        self.stdout.write("    * Encargado:  usuario: encargado1  | clave: Encargado2026!")
        self.stdout.write("    * Admin:      usuario: admin       | clave: Admin2026!")
