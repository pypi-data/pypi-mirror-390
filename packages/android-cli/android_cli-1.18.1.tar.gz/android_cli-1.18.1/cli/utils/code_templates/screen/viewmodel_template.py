def create_viewmodel(name, package):
    file_name = name + "ViewModel.kt"
    file_content = f'''package {package}

import androidx.lifecycle.viewModelScope
import com.astropaycard.android.core.base.base.viewmodel.BaseAction
import com.astropaycard.android.core.base.base.viewmodel.BaseViewModel
import com.astropaycard.android.core.base.base.viewmodel.BaseViewState
import com.astropaycard.android.core.ui.view_state.Type
import com.astropaycard.domain.analytics.Analytics
import kotlinx.coroutines.launch

class {name}ViewModel(
    private val analytics: Analytics,
) : BaseViewModel<{name}ViewModel.ViewState, {name}ViewModel.Action>(
    ViewState()
) {{

    override val viewModelName: String get() = "{name}ViewModel"

    override fun onLoadData() {{
        lastIntention = {{ onLoadData() }}
        sendAction(Action.Loading)
        viewModelScope.launch {{
            /*myAction().also {{
                val action = when (it) {{
                    is GetOpenBanks.Result.Error -> Action.Failure(message = it.value?.description)
                    is GetOpenBanks.Result.NetworkError -> Action.NetworkError
                    is GetOpenBanks.Result.Nothing -> Action.Nothing
                    is GetOpenBanks.Result.Success -> Action.Success
                }}
                sendAction(action)
            }}*/
        }}
    }}

    fun onClearDestination() {{
        sendAction(Action.DestinationChanged(null))
    }}

    fun onBack() {{
        sendAction(Action.DestinationChanged(Destination.Back))
    }}

    override fun onReduceState(viewAction: Action): ViewState = when (viewAction) {{
        is Action.Loading -> state.copy(
            loadState = Type.LoadLight
        )

        is Action.Failure -> state.copy(
            loadState = Type.DefaultError(viewAction.message),
        )

        is Action.NetworkError -> state.copy(
            loadState = Type.NetworkError,
        )

        is Action.Nothing -> state.copy(
            loadState = Type.ShowContent
        )

        is Action.DestinationChanged -> {{
            state.copy(
                destination = viewAction.destination,
            )
        }}

        is Action.Success -> {{
            state.copy(
                loadState = Type.ShowContent,
            )
        }}
    }}

    data class ViewState(
        val loadState: Type = Type.None,
        val destination: Destination? = null,
    ) : BaseViewState

    sealed class Action : BaseAction {{
        data object Loading : Action()
        data class Failure(
            val message: String? = null,
            val errorResourceId: Int = com.astropaycard.android.core.common.R.string.mobile_generic_error
        ) : Action()

        data object Success : Action()
        data object NetworkError : Action()
        data object Nothing : Action()
        data class DestinationChanged(val destination: Destination?) : Action()
    }}

    sealed class Destination {{
        data object Back : Destination()
    }}
}}
'''
    with open(file_name, "w") as file:
        file.write(file_content)
