import { ArrayFieldItemTemplateProps, ArrayFieldTemplateProps, getSubmitButtonOptions, SubmitButtonProps, WidgetProps } from '@rjsf/utils';
import { FormProps } from '@rjsf/core';
import { withTheme, ThemeProps } from '@rjsf/core';
import { Accordion, Badge, BadgeGroup, Button, Checkbox, TextInput } from '@dataesr/dsfr-plus';
import { ChangeEvent, FocusEvent } from 'react';
import { getInputProps, FieldTemplateProps, ObjectFieldTemplateProps, BaseInputTemplateProps } from '@rjsf/utils';

// Widgets
// const CustomTextWidget = (props: WidgetProps) => <TextInput onChange={(e) => props.onChange(e.target.value, null, props.id)} required={props.required} value={props.value} />;
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
      {errors}
    </div>
  );
}

function CustomObjectFieldTemplate(props: ObjectFieldTemplateProps) {
  const { title, description, properties } = props;
  return (
    <div>
      {description}
      <Accordion title={title} onClick={(e) => { e.preventDefault(); e.stopPropagation(); }}>
        {properties.map((element) => (
          <div className='property-wrapper'>{element.content}</div>
        ))}
      </Accordion>
    </div>
  );
}

function CustomArrayFieldTemplate(props: ArrayFieldTemplateProps) {
  const { title, items, canAdd, onAddClick, rawErrors } = props;
  return (
    <div>
      {title}
      <br />
      {items.map((element) => element)}
      {canAdd && <Button className="fr-mt-1w" size="sm" variant="secondary" onClick={onAddClick}>Add</Button>}
      {rawErrors?.length > 0 && <p>{rawErrors?.join(', ')}</p>}
    </div>
  )
}

function CustomSubmitButton(props: SubmitButtonProps) {
  const { uiSchema } = props;
  const { norender, submitText } = getSubmitButtonOptions(uiSchema)
  if (norender) return null

  return (
    <Button className="fr-mt-2w" variant="secondary">{submitText || "Submit"}</Button>
  )
}

// Theme
// const theme: ThemeProps = { widgets: { TextWidget: CustomTextWidget, CheckboxWidget: CustomCheckboxWidget } };
const theme: ThemeProps = { templates: { ButtonTemplates: { SubmitButton: CustomSubmitButton }, FieldTemplate: CustomFieldTemplate, BaseInputTemplate: CustomInputTemplate, ObjectFieldTemplate: CustomObjectFieldTemplate, ArrayFieldTemplate: CustomArrayFieldTemplate }, widgets: { CheckboxWidget: CustomCheckboxWidget } };
const ThemedForm = withTheme(theme);

export default function JsonSchemaForm(props: FormProps) {
  return <ThemedForm {...props} />;
}