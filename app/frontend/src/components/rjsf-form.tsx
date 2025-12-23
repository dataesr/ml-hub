import { WidgetProps } from '@rjsf/utils';
import { FormProps } from '@rjsf/core';
import { withTheme, ThemeProps } from '@rjsf/core';
import { Checkbox, TextInput } from '@dataesr/dsfr-plus';
import { ChangeEvent, FocusEvent } from 'react';
import { getInputProps, FieldTemplateProps, RJSFSchema, BaseInputTemplateProps } from '@rjsf/utils';
import validator from '@rjsf/validator-ajv8';
import CheckboxWidget from '@rjsf/core/lib/components/widgets/CheckboxWidget.js';

// Widgets
const CustomTextWidget = (props: WidgetProps) => <TextInput onChange={(e) => props.onChange(e.target.value, null, props.id)} required={props.required} value={props.value} />;
const CustomCheckboxWidget = (props: WidgetProps) => <Checkbox size="sm" required={props.required} checked={props.value} onChange={props.onChange} label={props.label} />;

// Template 
function CustomInputTemplate(props: BaseInputTemplateProps) {
  const {
    schema,
    id,
    options,
    label,
    value,
    type,
    placeholder,
    required,
    disabled,
    readonly,
    autofocus,
    onChange,
    onChangeOverride,
    onBlur,
    onFocus,
    rawErrors,
    hideError,
    uiSchema,
    registry,
    ...rest
  } = props;
  const onTextChange = ({ target: { value: val } }: ChangeEvent<HTMLInputElement>) => {
    // Use the options.emptyValue if it is specified and newVal is also an empty string
    onChange(val === '' ? options.emptyValue || '' : val);
  };
  const onTextBlur = ({ target: { value: val } }: FocusEvent<HTMLInputElement>) => onBlur(id, val);
  const onTextFocus = ({ target: { value: val } }: FocusEvent<HTMLInputElement>) => onFocus(id, val);

  const inputProps = { ...rest, ...getInputProps(schema, type, options) };
  const hasError = rawErrors?.length > 0 && !hideError;

  return (
    <TextInput
      className="fr-mb-2w"
      id={id}
      label={label}
      value={value}
      placeholder={placeholder}
      disabled={disabled}
      readOnly={readonly}
      autoFocus={autofocus}
      required={required}
      onChange={onChangeOverride || onTextChange}
      onBlur={onTextBlur}
      onFocus={onTextFocus}
      messageType={hasError ? 'error' : undefined}
      message={rawErrors?.join(', ') || undefined}
      type={typeof value === 'number' ? 'number' : 'text'}
      {...inputProps}
    />
  );
}

function CustomFieldTemplate(props: FieldTemplateProps) {
  const { classNames, style, help, description, errors, children } = props;
  return (
    <div className={classNames} style={style}>
      {description}
      {children}
      {help}
    </div>
  );
}

// Theme
// const theme: ThemeProps = { widgets: { TextWidget: CustomTextWidget, CheckboxWidget: CustomCheckboxWidget } };
const theme: ThemeProps = { templates: { FieldTemplate: CustomFieldTemplate, BaseInputTemplate: CustomInputTemplate }, widgets: { CheckboxWidget: CustomCheckboxWidget } };
const ThemedForm = withTheme(theme);

export default function JsonSchemaForm(props: FormProps) {
  return <ThemedForm {...props} />;
}