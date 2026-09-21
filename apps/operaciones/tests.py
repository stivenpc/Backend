from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.usuarios.models import PerfilUsuario
from apps.operaciones.models import Material, LoteMaterial, EstudioPrevio, Maquina, Proceso, RegistroMerma
from apps.auditoria.models import LogAuditoria

class TestSistemaMermaFundicion(TestCase):
    def setUp(self):
        # Crear grupos
        self.grupo_op = Group.objects.create(name='Operador')
        self.grupo_sup = Group.objects.create(name='Supervisor')
        self.grupo_enc = Group.objects.create(name='Encargado')

        # Crear usuarios con perfiles y roles RBAC (M2)
        self.user_op = User.objects.create_user(username='operador_test', password='Password123!', first_name='Operador')
        self.user_op.perfil.rol = 'OPERADOR'
        self.user_op.perfil.save()
        self.user_op.groups.add(self.grupo_op)

        self.user_sup = User.objects.create_user(username='supervisor_test', password='Password123!', first_name='Supervisor')
        self.user_sup.perfil.rol = 'SUPERVISOR'
        self.user_sup.perfil.save()
        self.user_sup.groups.add(self.grupo_sup)

        # Catálogos base
        self.material = Material.objects.create(codigo='AL-TEST', nombre='Aluminio Test', densidad_g_cm3=Decimal('2.70'), punto_fusion_c=660)
        self.maquina = Maquina.objects.create(codigo='MAQ-01', nombre='Horno Fusión 1', tipo='Horno')
        self.proceso = Proceso.objects.create(codigo='PROC-01', nombre='Fusión')

        # Lote de prueba
        self.lote = LoteMaterial.objects.create(
            codigo_lote='LOT-TEST-001',
            material=self.material,
            peso_inicial_kg=Decimal('500.00'),
            proveedor='Proveedor Test'
        )

        self.client = Client()

    def test_01_calculo_automatico_contenido_restante(self):
        """M1: Comprueba que el cálculo del contenido restante y merma acumulada sea automático y exacto."""
        # Crear estudio aprobado
        EstudioPrevio.objects.create(
            lote=self.lote,
            peso_calibrado_kg=Decimal('500.00'),
            estado='APROBADO',
            responsable_estudio=self.user_op,
            supervisor_aprobador=self.user_sup
        )

        # Saldo inicial
        self.assertEqual(self.lote.peso_restante_kg, Decimal('500.00'))
        self.assertEqual(self.lote.total_merma_kg, Decimal('0.00'))

        # Registrar primera merma de 50 kg
        RegistroMerma.objects.create(
            lote=self.lote,
            proceso=self.proceso,
            maquina=self.maquina,
            peso_merma_kg=Decimal('50.00'),
            tipo_merma='ESCORIA',
            operador=self.user_op
        )

        # Verificar balances
        self.assertEqual(self.lote.total_merma_kg, Decimal('50.00'))
        self.assertEqual(self.lote.peso_restante_kg, Decimal('450.00'))
        self.assertEqual(self.lote.porcentaje_merma_actual, Decimal('10.00'))

        # Registrar segunda merma de 25.50 kg
        RegistroMerma.objects.create(
            lote=self.lote,
            proceso=self.proceso,
            maquina=self.maquina,
            peso_merma_kg=Decimal('25.50'),
            tipo_merma='VIRUTA',
            operador=self.user_op
        )

        self.assertEqual(self.lote.total_merma_kg, Decimal('75.50'))
        self.assertEqual(self.lote.peso_restante_kg, Decimal('424.50'))
        self.assertEqual(self.lote.porcentaje_merma_actual, Decimal('15.10'))

    def test_02_bloqueo_gatekeeper_sin_estudio_previo(self):
        """M5: Comprueba que no se puede registrar merma si no existe estudio previo aprobado."""
        merma = RegistroMerma(
            lote=self.lote,  # Lote sin estudio previo
            proceso=self.proceso,
            maquina=self.maquina,
            peso_merma_kg=Decimal('10.00'),
            tipo_merma='ESCORIA',
            operador=self.user_op
        )
        with self.assertRaises(ValidationError) as ctx:
            merma.clean()
        self.assertIn("VALIDACIÓN DE ESTUDIO PREVIO OBLIGATORIO", str(ctx.exception))

    def test_03_bloqueo_gatekeeper_con_estudio_en_revision(self):
        """M5: Comprueba que el estudio en estado 'EN_REVISION' tampoco permite registrar mermas."""
        EstudioPrevio.objects.create(
            lote=self.lote,
            peso_calibrado_kg=Decimal('500.00'),
            estado='EN_REVISION',
            responsable_estudio=self.user_op
        )
        merma = RegistroMerma(
            lote=self.lote,
            proceso=self.proceso,
            maquina=self.maquina,
            peso_merma_kg=Decimal('10.00'),
            tipo_merma='ESCORIA',
            operador=self.user_op
        )
        with self.assertRaises(ValidationError) as ctx:
            merma.clean()
        self.assertIn("VALIDACIÓN DE ESTUDIO PREVIO OBLIGATORIO", str(ctx.exception))

    def test_04_bloqueo_merma_excede_saldo_disponible(self):
        """M1 / Criterio 2.1.3: Comprueba que no se pueda registrar una merma superior al remanente disponible."""
        EstudioPrevio.objects.create(
            lote=self.lote,
            peso_calibrado_kg=Decimal('500.00'),
            estado='APROBADO',
            responsable_estudio=self.user_op,
            supervisor_aprobador=self.user_sup
        )
        # Intentar registrar merma de 600 kg cuando el lote es de 500 kg
        merma = RegistroMerma(
            lote=self.lote,
            proceso=self.proceso,
            maquina=self.maquina,
            peso_merma_kg=Decimal('600.00'),
            tipo_merma='ESCORIA',
            operador=self.user_op
        )
        with self.assertRaises(ValidationError) as ctx:
            merma.clean()
        self.assertIn("excede el saldo restante", str(ctx.exception))

    def test_05_seguridad_rbac_operador_restringido(self):
        """M2 / Criterio 2.1.4: Comprueba que un Operador no pueda acceder a rutas de creación de lotes."""
        self.client.login(username='operador_test', password='Password123!')
        response = self.client.get(reverse('operaciones:lote_create'))
        # Redirige al dashboard porque no tiene rol SUPERVISOR ni ENCARGADO
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('operaciones:dashboard'), response.url)

    def test_06_supervisor_puede_aprobar_estudio(self):
        """M2 y M5: Comprueba que el supervisor tiene acceso a la vista de aprobación de estudio previo."""
        estudio = EstudioPrevio.objects.create(
            lote=self.lote,
            peso_calibrado_kg=Decimal('500.00'),
            estado='EN_REVISION',
            responsable_estudio=self.user_op
        )
        self.client.login(username='supervisor_test', password='Password123!')
        response = self.client.post(reverse('operaciones:estudio_aprobar', kwargs={'pk': estudio.pk}), {
            'estado': 'APROBADO',
            'observaciones_metrologicas': 'Aprobado formalmente por supervisor.'
        })
        self.assertEqual(response.status_code, 302)
        estudio.refresh_from_db()
        self.assertEqual(estudio.estado, 'APROBADO')
        self.assertEqual(estudio.supervisor_aprobador, self.user_sup)
