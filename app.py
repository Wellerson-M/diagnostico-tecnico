"""
Sistema Especialista de Diagnóstico Técnico
Backward Chaining com visualização do raciocínio
"""

import streamlit as st

st.set_page_config(page_title="Diagnóstico Técnico", layout="wide")


# =============================================================================
# BASE DE CONHECIMENTO — 20 REGRAS
# =============================================================================
REGRAS = [
    {
        "id": "R1",
        "categoria": "Energia",
        "condicoes": {"liga": "não", "led_placa": "não"},
        "diagnostico": "Problema na fonte de alimentação",
        "solucao": "Verifique se a fonte está conectada à tomada e o botão traseiro está ligado. Teste outra tomada. Se persistir, a fonte precisa ser testada ou substituída.",
    },
    {
        "id": "R2",
        "categoria": "Energia",
        "condicoes": {"liga": "não", "led_placa": "sim"},
        "diagnostico": "Problema no botão liga/desliga ou cabos da placa-mãe",
        "solucao": "Abra o gabinete e confira se o cabo do botão Power está corretamente conectado aos pinos da placa-mãe.",
    },
    {
        "id": "R3",
        "categoria": "Energia",
        "condicoes": {"liga": "sim", "desliga_sozinho": "sim"},
        "diagnostico": "Fonte insuficiente ou superaquecimento crítico",
        "solucao": "Monitore a temperatura com HWMonitor. Se passar de 90°C, é superaquecimento. Caso contrário, a fonte pode estar fraca.",
    },
    {
        "id": "R4",
        "categoria": "Vídeo",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "não",
            "bipes": "sim",
        },
        "diagnostico": "Falha de memória RAM ou placa de vídeo",
        "solucao": "Conte o padrão de bipes e consulte o manual da placa-mãe. Reencaixe a memória RAM ou teste com um pente por vez.",
    },
    {
        "id": "R5",
        "categoria": "Vídeo",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "não",
            "bipes": "não",
        },
        "diagnostico": "Problema na conexão do monitor ou placa de vídeo",
        "solucao": "Verifique o cabo do monitor. Teste outra saída de vídeo. Se há placa dedicada, teste removendo-a.",
    },
    {
        "id": "R6",
        "categoria": "Vídeo",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "sim",
        },
        "diagnostico": "Placa de vídeo defeituosa ou cabo danificado",
        "solucao": "Listras ou manchas indicam GPU em falha ou cabo ruim. Teste outro cabo primeiro.",
    },
    {
        "id": "R7",
        "categoria": "Sistema",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "sim",
        },
        "diagnostico": "Erro crítico do sistema (Blue Screen)",
        "solucao": "Anote o código de erro. Causas comuns: drivers desatualizados, RAM defeituosa, HD com setores ruins.",
    },
    {
        "id": "R8",
        "categoria": "Sistema",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "não",
            "boot_completa": "não",
        },
        "diagnostico": "Sistema operacional corrompido",
        "solucao": "PC liga mas Windows não carrega. Tente Modo de Recuperação (F8 ou F11). Se não funcionar, reinstale o sistema.",
    },
    {
        "id": "R9",
        "categoria": "Performance",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "não",
            "boot_completa": "sim",
            "lentidao": "sim",
            "temperatura": "alta",
        },
        "diagnostico": "Superaquecimento causando throttling",
        "solucao": "Limpe a poeira do cooler. Troque a pasta térmica se tiver mais de 2 anos. Confira se as ventoinhas estão girando.",
    },
    {
        "id": "R10",
        "categoria": "Performance",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "não",
            "boot_completa": "sim",
            "lentidao": "sim",
            "temperatura": "normal",
            "muitos_programas": "sim",
        },
        "diagnostico": "Excesso de programas em segundo plano",
        "solucao": "Abra o Gerenciador de Tarefas e finalize processos desnecessários. Desative inicializações automáticas.",
    },
    {
        "id": "R11",
        "categoria": "Performance",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "não",
            "boot_completa": "sim",
            "lentidao": "sim",
            "temperatura": "normal",
            "muitos_programas": "não",
            "disco_cheio": "sim",
        },
        "diagnostico": "Disco principal próximo da capacidade máxima",
        "solucao": "Windows precisa de 15% livre no C:. Use Limpeza de Disco, desinstale programas ou expanda o armazenamento.",
    },
    {
        "id": "R12",
        "categoria": "Performance",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "não",
            "boot_completa": "sim",
            "lentidao": "sim",
            "temperatura": "normal",
            "muitos_programas": "não",
            "disco_cheio": "não",
        },
        "diagnostico": "Possível malware ou disco com setores ruins",
        "solucao": "Faça varredura com Windows Defender. Rode 'chkdsk /f /r' no Prompt como admin para checar o disco.",
    },
    {
        "id": "R13",
        "categoria": "Rede",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "não",
            "boot_completa": "sim",
            "lentidao": "não",
            "internet": "lenta",
        },
        "diagnostico": "Conexão de internet lenta",
        "solucao": "Reinicie o roteador (30s sem energia). Teste velocidade em fast.com. Se outros dispositivos também estão lentos é o provedor.",
    },
    {
        "id": "R14",
        "categoria": "Rede",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "não",
            "boot_completa": "sim",
            "lentidao": "não",
            "internet": "sem",
            "tipo_conexao": "wifi",
        },
        "diagnostico": "Problema na conexão Wi-Fi",
        "solucao": "Esqueça a rede e conecte de novo. Atualize o driver Wi-Fi. Em último caso rode 'netsh winsock reset' como admin.",
    },
    {
        "id": "R15",
        "categoria": "Rede",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "não",
            "boot_completa": "sim",
            "lentidao": "não",
            "internet": "sem",
            "tipo_conexao": "cabo",
        },
        "diagnostico": "Problema no cabo Ethernet ou porta de rede",
        "solucao": "Veja se o LED da porta pisca. Troque o cabo e teste outra porta do roteador.",
    },
    {
        "id": "R16",
        "categoria": "Áudio",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "não",
            "boot_completa": "sim",
            "lentidao": "não",
            "internet": "ok",
            "som": "não",
        },
        "diagnostico": "Problema com drivers de áudio",
        "solucao": "Botão direito no ícone do som → Solução de problemas. Atualize drivers de áudio. Verifique a saída selecionada.",
    },
    {
        "id": "R17",
        "categoria": "Periféricos",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "não",
            "boot_completa": "sim",
            "lentidao": "não",
            "internet": "ok",
            "som": "ok",
            "perifericos": "não",
        },
        "diagnostico": "Problema com USB ou drivers de periféricos",
        "solucao": "Teste o dispositivo em outras portas USB. Reinstale drivers do chipset da placa-mãe.",
    },
    {
        "id": "R18",
        "categoria": "Hardware",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "não",
            "boot_completa": "sim",
            "lentidao": "não",
            "internet": "ok",
            "som": "ok",
            "perifericos": "ok",
            "ruido": "sim",
        },
        "diagnostico": "Ventoinha defeituosa ou HD em falha",
        "solucao": "Cliques metálicos no HD = falha iminente, faça backup imediato. Ruído contínuo geralmente é ventoinha.",
    },
    {
        "id": "R19",
        "categoria": "Sistema",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "não",
            "boot_completa": "sim",
            "lentidao": "não",
            "internet": "ok",
            "som": "ok",
            "perifericos": "ok",
            "ruido": "não",
            "update_travado": "sim",
        },
        "diagnostico": "Windows Update travado",
        "solucao": "Configurações → Solução de Problemas → Windows Update. Como admin: 'net stop wuauserv && net stop bits' e depois 'net start'.",
    },
    {
        "id": "R20",
        "categoria": "OK",
        "condicoes": {
            "liga": "sim",
            "desliga_sozinho": "não",
            "imagem": "sim",
            "defeito_visual": "não",
            "tela_azul": "não",
            "boot_completa": "sim",
            "lentidao": "não",
            "internet": "ok",
            "som": "ok",
            "perifericos": "ok",
            "ruido": "não",
            "update_travado": "não",
        },
        "diagnostico": "Nenhum problema crítico identificado",
        "solucao": "Seu computador parece estar funcionando dentro do esperado.",
    },
]


PERGUNTAS = {
    "liga": {
        "texto": "O computador liga (ventoinhas, LEDs)?",
        "opcoes": ["sim", "não"],
    },
    "led_placa": {
        "texto": "Algum LED da placa-mãe ou gabinete acende ao apertar o botão?",
        "opcoes": ["sim", "não"],
    },
    "desliga_sozinho": {
        "texto": "O computador desliga ou reinicia sozinho durante o uso?",
        "opcoes": ["sim", "não"],
    },
    "imagem": {"texto": "Aparece imagem no monitor?", "opcoes": ["sim", "não"]},
    "bipes": {
        "texto": "Você ouve bipes vindos do gabinete ao ligar?",
        "opcoes": ["sim", "não"],
    },
    "defeito_visual": {
        "texto": "A imagem tem defeitos visuais (listras, manchas, cores erradas)?",
        "opcoes": ["sim", "não"],
    },
    "tela_azul": {
        "texto": "O sistema apresenta tela azul (BSOD)?",
        "opcoes": ["sim", "não"],
    },
    "boot_completa": {
        "texto": "O Windows carrega completamente até a tela inicial?",
        "opcoes": ["sim", "não"],
    },
    "lentidao": {
        "texto": "O computador está lento ou travando?",
        "opcoes": ["sim", "não"],
    },
    "temperatura": {
        "texto": "Como está a temperatura (gabinete quente = alta)?",
        "opcoes": ["normal", "alta"],
    },
    "muitos_programas": {
        "texto": "Há muitos programas em segundo plano?",
        "opcoes": ["sim", "não"],
    },
    "disco_cheio": {
        "texto": "O disco principal (C:) está com menos de 15% livre?",
        "opcoes": ["sim", "não"],
    },
    "internet": {
        "texto": "Como está a conexão com a internet?",
        "opcoes": ["ok", "lenta", "sem"],
    },
    "tipo_conexao": {
        "texto": "Você está usando Wi-Fi ou cabo Ethernet?",
        "opcoes": ["wifi", "cabo"],
    },
    "som": {"texto": "O som está funcionando normalmente?", "opcoes": ["ok", "não"]},
    "perifericos": {
        "texto": "Os periféricos (teclado, mouse, USB) funcionam?",
        "opcoes": ["ok", "não"],
    },
    "ruido": {
        "texto": "O computador faz ruídos estranhos (cliques, estalos)?",
        "opcoes": ["sim", "não"],
    },
    "update_travado": {
        "texto": "O Windows Update está travado ou com erros?",
        "opcoes": ["sim", "não"],
    },
}


# =============================================================================
# MOTOR DE INFERÊNCIA
# =============================================================================
def buscar_diagnostico(respostas):
    """Retorna a primeira regra cujas condições foram TOTALMENTE satisfeitas."""
    for regra in REGRAS:
        if all(respostas.get(k) == v for k, v in regra["condicoes"].items()):
            return regra
    return None


def hipoteses_ativas(respostas):
    """Retorna regras que ainda podem ser verdadeiras (nenhuma condição contradita)."""
    ativas = []
    for regra in REGRAS:
        valida = all(
            not (k in respostas and respostas[k] != v)
            for k, v in regra["condicoes"].items()
        )
        if valida:
            ativas.append(regra)
    return ativas


def hipoteses_descartadas(respostas):
    """Retorna regras eliminadas + o motivo (qual resposta as descartou)."""
    descartadas = []
    for regra in REGRAS:
        for k, v in regra["condicoes"].items():
            if k in respostas and respostas[k] != v:
                descartadas.append(
                    {
                        "regra": regra,
                        "motivo": f"{k} = '{respostas[k]}' (esperava '{v}')",
                    }
                )
                break
    return descartadas


def proxima_pergunta(respostas):
    """Backward chaining: escolhe a próxima pergunta entre as hipóteses ainda válidas."""
    relevantes = []
    for regra in hipoteses_ativas(respostas):
        for k in regra["condicoes"].keys():
            if k not in respostas and k not in relevantes:
                relevantes.append(k)
    return relevantes[0] if relevantes else None


# =============================================================================
# INTERFACE
# =============================================================================
st.title("Sistema Especialista de Diagnóstico Técnico")
st.caption("Backward Chaining com visualização do raciocínio em tempo real")

if "respostas" not in st.session_state:
    st.session_state.respostas = {}
if "finalizado" not in st.session_state:
    st.session_state.finalizado = False

col_top1, col_top2 = st.columns([3, 1])
with col_top2:
    if st.button("Reiniciar", use_container_width=True):
        st.session_state.respostas = {}
        st.session_state.finalizado = False
        st.rerun()

st.divider()

# Layout principal: pergunta à esquerda, raciocínio à direita
col_principal, col_raciocinio = st.columns([1, 1])

with col_principal:
    if not st.session_state.finalizado:
        diagnostico = buscar_diagnostico(st.session_state.respostas)

        if diagnostico:
            st.session_state.finalizado = True
            st.rerun()
        else:
            prox = proxima_pergunta(st.session_state.respostas)
            if prox is None:
                st.warning("Não foi possível chegar a um diagnóstico.")
                st.session_state.finalizado = True
                st.rerun()
            else:
                pergunta = PERGUNTAS[prox]
                st.subheader("Pergunta atual")
                st.markdown(f"### {pergunta['texto']}")
                opcoes = pergunta["opcoes"]
                cols = st.columns(len(opcoes))
                for i, opcao in enumerate(opcoes):
                    with cols[i]:
                        if st.button(
                            opcao.capitalize(),
                            use_container_width=True,
                            key=f"btn_{prox}_{opcao}",
                            type="primary",
                        ):
                            st.session_state.respostas[prox] = opcao
                            st.rerun()

    if st.session_state.finalizado:
        diagnostico = buscar_diagnostico(st.session_state.respostas)
        if diagnostico:
            st.success(f"### {diagnostico['diagnostico']}")
            st.info(f"**Solução:**\n\n{diagnostico['solucao']}")
            st.caption(
                f"Categoria: **{diagnostico['categoria']}**  |  Regra: **{diagnostico['id']}**"
            )
        else:
            st.error("Diagnóstico não encontrado.")


# =============================================================================
# PAINEL DE RACIOCÍNIO (lado direito)
# =============================================================================
with col_raciocinio:
    st.subheader("O que o sistema está pensando")

    ativas = hipoteses_ativas(st.session_state.respostas)
    descartadas = hipoteses_descartadas(st.session_state.respostas)

    # Barra de progresso visual
    total = len(REGRAS)
    eliminadas = len(descartadas)
    progresso = eliminadas / total if total > 0 else 0
    st.progress(progresso, text=f"Hipóteses restantes: {len(ativas)} de {total}")

    # Hipóteses ainda em análise
    st.markdown(f"#### Hipóteses ativas ({len(ativas)})")
    if ativas:
        with st.container(border=True):
            for regra in ativas[:8]:
                st.markdown(f"• **[{regra['id']}]** {regra['diagnostico']}")
                st.caption(f"  → categoria: {regra['categoria']}")
            if len(ativas) > 8:
                st.caption(f"... e mais {len(ativas) - 8} hipóteses")
    else:
        st.info("Nenhuma hipótese ativa.")

    # Hipóteses já descartadas
    if descartadas:
        with st.expander(f"Hipóteses descartadas ({len(descartadas)})", expanded=False):
            for d in descartadas:
                st.markdown(
                    f"• ~~**[{d['regra']['id']}]** {d['regra']['diagnostico']}~~"
                )
                st.caption(f"  Eliminada por: `{d['motivo']}`")


# =============================================================================
# SIDEBAR — memória de trabalho
# =============================================================================
with st.sidebar:
    st.header("Memória de Trabalho")
    st.caption("Fatos coletados durante a análise")
    if st.session_state.respostas:
        for k, v in st.session_state.respostas.items():
            st.write(f"• **{k}** = `{v}`")
    else:
        st.caption("Vazia. Aguardando primeira resposta.")

    st.divider()
    st.header("Sobre o sistema")
    st.caption(f"**Base de conhecimento:** {len(REGRAS)} regras")
    st.caption("**Motor de inferência:** Backward Chaining")
    st.caption("**Categorias cobertas:**")
    st.caption("⚡ Energia • 🖥️ Vídeo • 💻 Sistema")
    st.caption("⚙️ Performance • 🌐 Rede • 🔊 Áudio")
    st.caption("🖱️ Periféricos • 🔧 Hardware • ✅ OK")
