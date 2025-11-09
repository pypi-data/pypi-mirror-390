import re


def create_fragment(name, package):
    file_name = name + "Fragment.kt"
    screen_name = re.sub(r"([A-Z])", r"_\1", name)[1:].upper()
    file_content = f'''package {package}

import android.os.Bundle
import android.view.View
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.livedata.observeAsState
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.PreviewParameter
import androidx.navigation.fragment.navArgs
import com.astropaycard.android.core.base.base.fragment.BaseFragment
import com.astropaycard.android.core.base.extensions.navigateBack
import com.astropaycard.android.core.design_system.previews.DefaultPreview
import com.astropaycard.android.core.design_system.theme.ElviraTheme
import com.astropaycard.android.core.design_system.texts.Base600
import com.astropaycard.android.core.ui.databinding.FragmentComposeBinding
import com.astropaycard.android.core.ui.toolbar.DefaultToolBar
import com.astropaycard.android.core.ui.view_state.ContentState
import {package}.mock_preview.{name}PreviewProvider
import org.koin.androidx.viewmodel.ext.android.viewModel

class {name}Fragment :
    BaseFragment<FragmentComposeBinding>(FragmentComposeBinding::inflate) {{
    override val fragmentName = "{name}Fragment"
    override val screenName = "{screen_name}"

    private val viewModel: {name}ViewModel by viewModel()

    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        viewModel.loadData()
    }}

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {{
        super.onViewCreated(view, savedInstanceState)

        binding.apply {{
            composeView.setContent {{
                ElviraTheme {{
                    val screenState by viewModel.stateLiveData.observeAsState(
                        initial = {name}ViewModel.ViewState()
                    )
                    Screen(
                        screenState = screenState,
                        eventReducer = ::onUIEvent,
                    )
                }}
            }}
        }}
    }}

    @Composable
    private fun Screen(
        screenState: {name}ViewModel.ViewState,
        eventReducer: (UIEvent) -> Unit = {{}},
    ) {{
        screenState.destination?.let {{
            Navigation(it)
        }}

        ContentState(
            state = screenState.loadState,
            lastIntention = {{ viewModel.lastIntention() }},
            toolbar = {{
                DefaultToolBar(
                    title = "TODO: lokaliseResource(...)"
                )
            }},
            content = {{
                Content(
                    screenState = screenState,
                    eventReducer = eventReducer,
                )
            }},
            floatingButton = {{}}
        )
    }}

    @Composable
    private fun Content(
        screenState: {name}ViewModel.ViewState,
        eventReducer: (UIEvent) -> Unit
    ) {{
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ){{
            Base600(text = "{name}")
        }}
    }}

    @Composable
    private fun Navigation(destination: {name}ViewModel.Destination) {{
        when (destination) {{
            is {name}ViewModel.Destination.Back -> navigateBack()
        }}
        
        viewModel.onClearDestination()
    }}

    private sealed class UIEvent {{
        data object Back : UIEvent()
    }}

    private fun onUIEvent(event: UIEvent) {{
        when (event) {{
            is UIEvent.Back -> viewModel.onBack()
        }}
    }}

    @Composable
    @DefaultPreview
    private fun ScreenPreview(
        @PreviewParameter({name}PreviewProvider::class) state: {name}ViewModel.ViewState
    ) {{
        ElviraTheme {{
            Screen(state)
        }}
    }}
}}
'''
    with open(file_name, "w") as file:
        file.write(file_content)
