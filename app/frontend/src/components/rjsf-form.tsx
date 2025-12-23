import { WidgetProps } from '@rjsf/utils';
import { FormProps } from '@rjsf/core';
import { withTheme, ThemeProps } from '@rjsf/core';
import { Checkbox, TextInput } from '@dataesr/dsfr-plus';

// Widgets
const CustomTextWidget = (props: WidgetProps) => <TextInput onChange={(e) => props.onChange(e.target.value, null, props.id)} required={props.required} value={props.value} />;
const CustomCheckboxWidget = (props: WidgetProps) => <Checkbox size="sm" required={props.required} checked={props.value} onChange={props.onChange} label={props.label} />;

// Them
const theme: ThemeProps = { widgets: { TextWidget: CustomTextWidget, CheckboxWidget: CustomCheckboxWidget } };
const ThemedForm = withTheme(theme);

export default function JsonSchemaForm(props: FormProps) {
  return <ThemedForm {...props} />;
}