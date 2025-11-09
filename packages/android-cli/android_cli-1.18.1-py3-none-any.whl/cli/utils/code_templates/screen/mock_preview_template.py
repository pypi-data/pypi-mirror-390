import os


def create_mock_preview(name, package):
    os.mkdir("mock_preview")
    os.chdir("mock_preview")
    file_name = name + "PreviewProvider.kt"
    file_content = f'''package {package}.mock_preview

import androidx.compose.ui.tooling.preview.PreviewParameterProvider
import com.astropaycard.android.core.ui.view_state.Type
import {package}.{name}ViewModel


internal class {name}PreviewProvider :
    PreviewParameterProvider<{name}ViewModel.ViewState> {{
    override val values: Sequence<{name}ViewModel.ViewState>
        get() = sequenceOf(
            getState()
        )

    private fun getState() = {name}ViewModel.ViewState(
        loadState = Type.ShowContent,
    )

}}
'''
    with open(file_name, "w") as file:
        file.write(file_content)
