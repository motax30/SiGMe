from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .utils.cpf_validator import validate_cpf
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Create your models here.

from django.db import models

ROTEIRIZAR = 'ROTEIRIZAR_UNIDADES_ESTUDO'

PERMISSIONS_AND_ACTIONS = [
    (ROTEIRIZAR, 'ROTEIRIZAR_UNIDADES_ESTUDO'),
]


class Permissao(models.Model):
    """
    Entidade para controlar permissões
    """
    # pylint: disable=invalid-name
    id = models.CharField(
        'Permissão', max_length=255, primary_key=True,
        choices=PERMISSIONS_AND_ACTIONS
    )
    description = models.CharField(
        'Descrição', max_length=255, blank=True, null=True
    )
    active = models.BooleanField('Ativo', default=True)
    created = models.DateTimeField('Criado em', auto_now_add=True)
    modified = models.DateTimeField('Modificado em', auto_now=True)

    def __str__(self):
        if self.description:
            return self.description
        return self.id

    class Meta:
        """
        Classe Meta
        """
        verbose_name = 'Permissão'
        verbose_name_plural = 'Permissões'


class Funcao(models.Model):
    """
    Classe da entidade Funcao
    """

    nome = models.CharField(
        'Sigla', max_length=255
    )
    descricao_curta = models.CharField(
        'Descrição Curta da Função', max_length=255,
    )
    descricao_longa = models.CharField(
        'Descrição Longa da Função', max_length=255,
        blank=True, null=True,
    )
    dt_cadastro = models.DateTimeField(
        'Data de Cadastro', auto_now_add=True
    )
    pessoas = models.ManyToManyField(
        'User', related_name='funcoes', through='FuncaoPessoa'
    )
    permissoes = models.ManyToManyField(
        Permissao, verbose_name='Permissões', blank=True,
    )
    
    class Meta():
        verbose_name_plural='Funções'

    def __str__(self):
        return f'{self.nome}'
    

TIPO_ASSOCIACAO_INDETERMINADO = 0
TIPO_ASSOCIACAO_PERMANENTE = 1
TIPO_ASSOCIACAO_TEMPORARIO = 2


class FuncaoPessoa(models.Model):
    """
    Classe de configuração do modelo de Função Usuário
    """
    TIPO_ASSOCIACAO_CHOICES = (
        (TIPO_ASSOCIACAO_INDETERMINADO, ''),
        (TIPO_ASSOCIACAO_PERMANENTE, 'Permanente'),
        (TIPO_ASSOCIACAO_TEMPORARIO, 'Temporário'),
    )

    funcao = models.ForeignKey(Funcao, on_delete=models.CASCADE)

    usuario = models.ForeignKey('User', on_delete=models.CASCADE)

    tipo = models.PositiveIntegerField(
        choices=TIPO_ASSOCIACAO_CHOICES, default=TIPO_ASSOCIACAO_PERMANENTE
    )

    data_inicio = models.DateField(
        'Data Inicial', help_text='Início da vigência'
    )

    data_fim = models.DateField(
        'Data Final', help_text='Término da vigência',
        blank=True, null=True
    )

    def is_permanente(self):
        """
        Verifica se o tipo de associação é permanente
        """
        return self.tipo == TIPO_ASSOCIACAO_PERMANENTE

    def is_temporario(self):
        """
        Verifica se o tipo de associação é temporário
        """
        return self.tipo == TIPO_ASSOCIACAO_TEMPORARIO

    def is_ativo(self):
        """
        Verifica se a associação está vigente
        """
        today = timezone.now().date()

        return (
            self.data_inicio <= today
        ) and (
            self.data_fim is None or self.data_fim > today
        )

    def clean(self):
        # Caso a função seja temporária verifica se foi definida uma
        # data final
        if self.is_temporario() and not self.data_fim:
            raise ValidationError({
                'data_fim': 'É necessário definir uma data final para '
                            'funções temporárias.'
            })

        # Verifica se a data final é maior que a data inicial
        if self.data_fim and self.data_fim < self.data_inicio:
            raise ValidationError({
                'data_fim': 'Não pode ser menor que a data inicial.'
            })

    def get_associacoes_permanentes(self):
        """
        Retorna todas as associações permanentes desta função
        """
        today = timezone.now().date()

        funcoes_permanentes = FuncaoPessoa.objects.filter(
            funcao=self.funcao,
            tipo=TIPO_ASSOCIACAO_PERMANENTE
        ).exclude(
            data_fim__lt=today
        ).exclude(
            data_inicio__gt=today
        )

        if self.id:
            funcoes_permanentes = funcoes_permanentes.exclude(id=self.id)

    class Meta:
        """
        Configurações especiais de entidade
        """
        verbose_name = 'Associação'
        verbose_name_plural = 'Associações'


BRAZILIAN_STATES = [
    ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AP', 'Amapá'),
    ('AM', 'Amazonas'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'),
    ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PR', 'Paraná'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),
    ('SE', 'Sergipe'),
    ('TO', 'Tocantins'),
]

DOCUMENT_LIST = [
    ('ID_MILITAR', 'Carteira de Identidade Militar (RA, RE, RM)'),
    ('RG', 'Carteira de Identidade Civil (RG)'),
    ('CARTEIRA',
     'Carteira de Identificação de Orgão Fiscalizador (Ordens, Conselhos, etc)'
     ),
    ('Passaporte', 'Passaporte'),
    ('CARTEIRA_MIN_PUBLICO', 'Carteira Funcional do Ministério Público'),
    ('RESERVISTA', 'Certificado de Reservista'),
    ('CARTEIRA_FUNCIONAL)', 'Carteira Funcional Expedida por Órgão Público'),
    ('CTPS', 'Carteira de Trabalho e Previdência Social'),
    ('CNH', 'Carteira Nacional de Habilitação')
]

class User(AbstractUser):
    """ Classe base para a autenticação de usuários
    """
    name = models.CharField(
        "Nome", max_length=100
    )
    email = models.EmailField(
        'Endereço de email', unique=False
    )
    cpf = models.CharField(
        "CPF", unique=True, max_length=11, validators=[validate_cpf],
        blank=True, null=True
    )
    identity_document_type = models.CharField(
        "Tipo", max_length=30, blank=True, null=True, choices=DOCUMENT_LIST
    )
    identity_document_number = models.CharField(
        "Numero", max_length=15, blank=True, null=True
    )
    identity_document_issuer = models.CharField(
        "Orgão Emissor", max_length=15, blank=True, null=True
    )
    identity_document_uf = models.CharField(
        "UF", max_length=2, blank=True, null=True, choices=BRAZILIAN_STATES
    )
    identity_document_nationality = models.CharField(
        "País de Origem", max_length=10, blank=True, null=True
    )
    ldap_uid = models.CharField(
        "LDAP uid", max_length=255, blank=True, null=True
    )
    avatar = models.ImageField(
        'Avatar', blank=True, null=True
    )

# Meta
class MetaEstudo(models.Model):
    inicio = models.DateTimeField(
        'Data de Início'
    )
    termino = models.DateTimeField(
        'Data limite'
    )
    descricao = models.CharField(max_length=256)
    roteiros = models.ManyToManyField(
        "sigme_web.Roteiro"
    )
    
    class Meta:
        verbose_name='Meta de Estudo'
        verbose_name_plural="Metas de Estudo"
        
    def __str__(self):
        return self.descricao

    
# Roteiro
class Roteiro(models.Model):
    study_unit = models.ForeignKey(
        "sigme_web.UnidadeEstudo", 
        verbose_name=("Unidades de Estudo"),
        on_delete=models.CASCADE
    )
    disciplina = models.ForeignKey(
        "sigme_web.Disciplina",
        on_delete=models.CASCADE
    )
    
    class Meta:
        verbose_name='Roteiro de Estudo'
        verbose_name_plural="Roteiros de Estudo"
    
    def __str__(self):
        return f'{self.study_unit.name} - Referente à disciplina ({self.disciplina.name}).'
    
    
# Tarefa
class Tarefa(models.Model):
    descricao = models.CharField(_("Descrição"), max_length=256)
    duration = models.DurationField()
    
    class Meta:
        verbose_name='Tarefa'
        verbose_name_plural="Tarefas"
    
    def __str__(self):
        return self.descricao
    
# Disciplina
class Disciplina(models.Model):
    name = models.CharField(max_length=200)
    teacher = models.ManyToManyField(
        "sigme_web.User", verbose_name="associação")
    
    class Meta:
        verbose_name='Disciplina'
        verbose_name_plural="Disciplina"   
    
    def __str__(self):
        return self.name
        
# Unidade de Estudo(Partes unitárias de uma disciplina)
class UnidadeEstudo(models.Model):
    name = models.CharField(max_length=200)
    tarefas = models.ManyToManyField(
        "sigme_web.Tarefa", verbose_name=_("tarefas"))
    
    class Meta:
        verbose_name='Unidade de Estudo'
        verbose_name_plural="Unidades de Estudo"
    
    def __str__(self):
        return self.name
