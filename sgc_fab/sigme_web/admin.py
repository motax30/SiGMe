from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.admin.decorators import register
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from import_export.admin import ImportExportModelAdmin
from django.utils.translation import gettext_lazy as _
from django.db import models
from .models import Disciplina, Funcao, MetaEstudo, Roteiro, Tarefa, UnidadeEstudo, User

# Register your models here.

class FuncaoInLine(admin.TabularInline):
    """
    InLine da função
    """
    model = Funcao
    extra = 0


class FuncaoPessoaInLine(admin.TabularInline):
    """
    InLine de Pessoa
    """
    model = Funcao.pessoas.through
    extra = 0
    raw_id_fields = ('usuario', 'funcao')


class TeacherInLine(admin.TabularInline):
    """
    InLine de Pessoa
    """
    model = Disciplina.teacher.through
    verbose_name = 'Instrutor da Disciplina'
    verbose_name_plural = 'Instrutores da Disciplina'
    raw_id_fields = ('user',)
    extra = 1


class RoteiroInline(admin.TabularInline):
    '''Tabular Inline View for Roteiro'''

    model = MetaEstudo.roteiros.through
    extra = 0
    verbose_name='Roteiro de Estudo por Meta'
    verbose_name_plural='Roteiros de Estudo por Meta'


class TarefaInline(admin.TabularInline):
    '''Tabular InLine View for Tarefa'''
    model = UnidadeEstudo.tarefas.through
    list_display = ('descricao','duration')
    verbose_name_plural='Tarefas por Unidade de Estudo'
    raw_id_fields = ('tarefa',)
    extra = 0
   
    
@register(Funcao)
class FuncaoAdmin(ImportExportModelAdmin):
    """ Classe de configuração do modelo Função.
    """
    # pylint: disable= too-many-ancestors
    list_display = [
        'id', 'nome', 'descricao_curta', 'descricao_longa',
    ]
    search_fields = [
        'nome',
        'descricao_curta',
        'descricao_longa',
        'pessoas__username'
    ]
    inlines = [FuncaoPessoaInLine]


@register(User)
class UserAdmin(BaseUserAdmin, ImportExportModelAdmin):
    """ Classe para configuração de cadastratos de usuários via admin do Django
    """
    search_fields = ['username', 'email', 'name', 'cpf']
    filter_horizontal = [
        'groups',
        'user_permissions',
    ]

    fieldsets = (
        (None, {'fields': ('username', 'password', 'avatar')}),
        (_('Personal info'), {'fields': ('name', 'email', 'cpf',)}),
        ('Documento de Identificação', {'fields': (
            'identity_document_type', 'identity_document_number',
            'identity_document_issuer', 'identity_document_uf',
            'identity_document_nationality')}),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
            'classes': ['collapse']
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'name', 'email', 'cpf', 'username', 'password1', 'password2'
            ),
        }),
    )

    inlines = [FuncaoPessoaInLine]

   
@admin.register(MetaEstudo)
class MetaEstudoAdmin(admin.ModelAdmin):
    '''Admin View for MetaEstudo'''
    list_display = ['descricao','total_roteiros_por_meta']
    inlines = [
        RoteiroInline,
    ]
    exclude = ['roteiros']
    
    def total_roteiros_por_meta(self, obj):
        ps = MetaEstudo.objects.annotate(num_roteiros=models.Count('roteiros')).all()
        num_roteiros = None
        for p in ps:
            num_roteiros = p.num_roteiros
        return num_roteiros
    total_roteiros_por_meta.admin_order_field  = 'roteiros'  #Allows column order sorting
    total_roteiros_por_meta.short_description = 'Total de Roteiros'    
    
    
@admin.register(Roteiro)
class RoteiroAdmin(admin.ModelAdmin):
    '''Admin View for Roteiro'''
    list_display = ['__str__',]
    raw_id_fields = ['study_unit','disciplina']
    
    def get_name(self, obj):
        return obj.disciplina.name
    get_name.admin_order_field  = 'disciplina'  #Allows column order sorting
    get_name.short_description = 'Disciplina Praçinh'
     
@register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ['name',]
    inlines = [TeacherInLine,]
    exclude = ['teacher']

     
@register(UnidadeEstudo)
class UnidadeEstudoAdmin(admin.ModelAdmin):
    list_display = ['id','name',]
    inlines = [TarefaInline]
    exclude = ('tarefas',)
    
@register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ['id','descricao','duration',]  