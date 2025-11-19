import { useState } from "react"
import {
  Accordion,
  Alert,
  Button,
  Container,
  Modal,
  ModalContent,
  ModalFooter,
  ModalTitle,
  SegmentedControl,
  SegmentedElement,
  Select,
  SelectOption,
  Text,
  TextArea,
  TextInput,
  Title,
} from "@dataesr/dsfr-plus"
import { scrollToTop } from "../../utils"
import { useNavigate } from "react-router-dom"
import { Job, JobInputs } from "../../api/jobs/types"
import { createJob } from "../../api/jobs/api"
import { useGetDatasetConfig, useListDatasetConfigs } from "../../api/datasets/hooks"
import { SmartTextInput } from "../../components/inputs/smart-input"
import { validateAplhaNum, validateRepoName, validateText } from "../../helpers/validate"

const DEFAULT_INPUTS: JobInputs = {
  model_name: "",
  dataset_name: "",
  pipeline: "causallm",
  gpu: 1,
}

//TODO: split into several components
export default function EvaluateSubmit() {
  const [inputs, setInputs] = useState<JobInputs>(DEFAULT_INPUTS)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [alertError, setAlertError] = useState<string>("")
  const [alertSuccess, setAlertSuccess] = useState<string>("")
  const [openSubmit, setOpenSubmit] = useState<boolean>(false)

  const [controlConfig, setControlConfig] = useState<string>("custom")
  const { data: configs } = useListDatasetConfigs(inputs?.dataset_name)
  const { data: selectedConfig } = useGetDatasetConfig(inputs?.dataset_config, inputs?.dataset_name)

  console.log(controlConfig)

  const navigate = useNavigate()
  const required = inputs.model_name && inputs.dataset_name

  const resetInputs = () => {
    setInputs(DEFAULT_INPUTS)
    setErrors({})
    scrollToTop()
  }

  const handleErrorsChange = (key: string, message: string) => {
    if (message) {
      setErrors((prev) => ({ ...prev, [key]: message }))
    } else if (key in errors) {
      const { [key]: _, ...newErrors } = errors
      setErrors(newErrors)
    }
  }

  const handleInputsChange = (key: string, value: any) => {
    setInputs({ ...inputs, [key]: value })
    setAlertError("")
  }

  const onCheck = (e: React.FormEvent) => {
    e.preventDefault()
    if (Object.entries(errors).length) setAlertError("Please fix the errors before creating the job.")
    else setOpenSubmit(true)
  }

  const onSubmit = async () => {
    try {
      const newJob: Job = await createJob(inputs)
      resetInputs()
      setAlertSuccess(`Successfully created evaluation ${newJob.spec.name} (${newJob.id})`)
      setTimeout(() => navigate(`/evaluate`), 2000)
    } catch (error) {
      console.error("Error creating job:", error)
      setAlertError("Error creating job. Please try again.")
    }
  }

  // console.log("input", inputs)
  // console.log("errors", errors)

  return (
    <Container className="fr-my-3w">
      <Button size="sm" variant="tertiary" icon="arrow-left-line" onClick={() => navigate("/evaluate")}>
        Back to evaluations
      </Button>
      <Title as="h3" className="fr-mb-4w fr-mt-3w">
        New evaluation
      </Title>
      <Container fluid style={{ maxWidth: "600px" }}>
        <SmartTextInput
          value={inputs.model_name}
          onChange={(value) => handleInputsChange("model_name", value)}
          onError={(value) => handleErrorsChange("model_name", value)}
          validateSync={(value) => validateText(value, true)}
          validateAsync={(value) => validateRepoName(value, true, true)}
          label="Model Name"
          hint="HuggingFace repository of the model to train."
          placeholder="meta-llama/Llama-3.2-1B"
          required
        />
        <SmartTextInput
          value={inputs.dataset_name}
          onChange={(value) => handleInputsChange("dataset_name", value)}
          onError={(value) => handleErrorsChange("dataset_name", value)}
          validateSync={(value) => validateText(value, true)}
          label="Dataset Name"
          hint="HuggingFace repository or OVH file path of the dataset."
          placeholder="dataesr/training-dataset"
          required
        />
        <Select
          label="Evaluate Pipeline"
          selectedKey={inputs.pipeline}
          onSelectionChange={(key) => handleInputsChange("pipeline", key)}
          isRequired
        >
          <SelectOption key={"causallm"}>CausalLM</SelectOption>
          <SelectOption key={"causallm-unsloth"}>CausalLM with Unsloth</SelectOption>
        </Select>
        <SmartTextInput
          value={inputs.wandb_project || ""}
          onChange={(value) => handleInputsChange("wandb_project", value)}
          onError={(value) => handleErrorsChange("wandb_project", value)}
          validateSync={validateAplhaNum}
          label="Experiment Project Name"
          hint="Name of the experiment project. Defaults to 'uncategorized' if not set."
          placeholder="entity-extraction-acknowledgments"
        />
        <Accordion title="Dataset options">
          <SegmentedControl
            className="fr-mb-2w"
            name="datasetConfig"
            label="Dataset config"
            value={controlConfig}
            onChangeValue={(value) => {
              if (value === "custom") handleInputsChange("dataset_config", "")
              setControlConfig(value)
            }}
          >
            <SegmentedElement defaultChecked={true} value="custom" label="Custom" />
            <SegmentedElement value="existing" label="Existing" />
          </SegmentedControl>
          {controlConfig === "existing" && (
            <Container fluid>
              <Select
                label="Load config"
                defaultSelectedKey={"custom"}
                selectedKey={inputs?.dataset_config || "custom"}
                onSelectionChange={(key) => handleInputsChange("dataset_config", key)}
                isDisabled={!inputs?.dataset_name}
              >
                {configs &&
                  configs?.map((config) => <SelectOption key={config.config_name}>{config.config_name}</SelectOption>)}
              </Select>
              {selectedConfig && Object.entries(selectedConfig).map(([key, value]) => <Text>{`${key}: ${value}`}</Text>)}
            </Container>
          )}
          {controlConfig === "custom" && (
            <Container fluid>
              <Select
                label="Dataset prompts format"
                defaultSelectedKey={"auto"}
                selectedKey={inputs?.dataset_format || selectedConfig?.dataset_format || "auto"}
                onSelectionChange={(key) => handleInputsChange("dataset_format", key)}
              >
                <SelectOption key="auto">Auto</SelectOption>
                <SelectOption key="text">Text</SelectOption>
                <SelectOption key="conversational">Conversational</SelectOption>
              </Select>
              <TextArea
                style={{ resize: "vertical", maxHeight: "400px" }}
                className="fr-mt-2w"
                label="Dataset prompts instruction"
                hint="Custom instruction that will be applied to all prompts."
                value={inputs?.dataset_instruction || selectedConfig?.instruction || ""}
                placeholder="You are a helpful assistant..."
                onChange={(e) => handleInputsChange("dataset_instruction", e.target.value)}
                messageType={errors.dataset_instruction ? "error" : undefined}
                message={errors.dataset_instruction || undefined}
              />
              <TextInput
                className="fr-mt-2w"
                label="Dataset prompts text format"
                hint="Text format that will be applied to all prompts."
                value={inputs?.dataset_text_format || selectedConfig?.text_format || ""}
                placeholder="### Instruction:\n {instruction}..."
                onChange={(e) => handleInputsChange("dataset_text_format", e.target.value)}
                messageType={errors.dataset_text_format ? "error" : undefined}
                message={errors.dataset_text_format || undefined}
                disabled={inputs?.dataset_format === "conversational"}
              />
              {/* <TextInput
            className="fr-mt-2w"
            label="Dataset prompts chat template"
            hint="Chat template that will be applied to all prompts."
            value={inputs?.dataset_chat_template || selectedConfig?.chat_template || ""}
            placeholder="{%- for message in messages -%}..."
            onChange={(e) => handleInputsChange("dataset_chat_template", e.target.value)}
            messageType={errors.dataset_chat_template ? "error" : undefined}
            message={errors.dataset_chat_template || undefined}
          /> */}
            </Container>
          )}
          {/* <Toggle
            label="Link OVH dataset volume"
            checked={inputs?.dataset_volume || false}
            onChange={(e) => handleInputsChange("dataset_volume", e.target.checked)}
          /> */}
        </Accordion>
        {alertError && (
          <Alert
            className="fr-mt-4w"
            variant="error"
            title="Error"
            description={alertError}
            closeMode="controlled"
            onClose={() => setAlertError("")}
          />
        )}
        <div className="fr-mt-5w" style={{ display: "flex", width: "100%", alignItems: "center" }}>
          <div style={{ flexGrow: 1 }}>
            <Button variant="secondary" onClick={() => resetInputs()} disabled={inputs === DEFAULT_INPUTS}>
              Reset options
            </Button>
          </div>
          <Button onClick={onCheck} disabled={!required}>
            Evaluate
          </Button>
        </div>
        <Container fluid>
          <Modal isOpen={openSubmit} hide={() => null}>
            <ModalTitle>Confirm evaluation</ModalTitle>
            <ModalContent>
              <Text>Are you sure you want to submit the following evaluation ?</Text>
              {Object.entries(inputs).map(([key, value]) => (
                <Text className="fr-mb-1v fr-text--legend">{`- ${key}: ${String(value)}`}</Text>
              ))}
            </ModalContent>
            <ModalFooter>
              {alertSuccess ? (
                <Alert variant="success" title="Job created!" description={alertSuccess} />
              ) : (
                <div className="fr-mt-5w" style={{ display: "flex", width: "100%", alignItems: "center" }}>
                  <div style={{ flexGrow: 1 }}>
                    <Button variant="secondary" onClick={() => setOpenSubmit(false)}>
                      No
                    </Button>
                  </div>
                  <Button onClick={onSubmit}>Evaluate</Button>
                </div>
              )}
            </ModalFooter>
          </Modal>
        </Container>
      </Container>
    </Container>
  )
}
