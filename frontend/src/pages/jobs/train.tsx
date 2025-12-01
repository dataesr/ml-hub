import { useState } from "react"
import {
  Accordion,
  Alert,
  Button,
  Col,
  Container,
  Modal,
  ModalContent,
  ModalFooter,
  ModalTitle,
  Row,
  SegmentedControl,
  SegmentedElement,
  Select,
  SelectOption,
  Tag,
  TagGroup,
  Text,
  TextArea,
  TextInput,
  Title,
  Toggle,
} from "@dataesr/dsfr-plus"
import { scrollToTop } from "../../utils"
import { useNavigate } from "react-router-dom"
import { validateText, validateAplhaNum, validateRepoName } from "../../helpers/validate"
import { Job, JobTrainInputs } from "../../api/jobs/types"
import { createJobTrain } from "../../api/jobs/api"
import { useGetDatasetConfig, useListDatasetConfigs } from "../../api/datasets/hooks"
import { SmartTextInput } from "../../components/inputs/smart-input"

const DEFAULT_INPUTS: JobTrainInputs = {
  model_name: "",
  dataset_name: "",
  pipeline: "causallm",
  gpu: 1,
}

//TODO: split into several components
export default function JobsTrain() {
  const [inputs, setInputs] = useState<JobTrainInputs>(DEFAULT_INPUTS)
  const [pushToHF, setPushToHF] = useState<boolean>(true)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [alertError, setAlertError] = useState<string>("")
  const [alertSuccess, setAlertSuccess] = useState<string>("")
  const [openSubmit, setOpenSubmit] = useState<boolean>(false)
  const [trainingArg, setTrainingArg] = useState<{ key: string; value: string }>(null)

  const [controlConfig, setControlConfig] = useState<string>("custom")
  const { data: configs } = useListDatasetConfigs(inputs?.dataset_name)
  const { data: selectedConfig } = useGetDatasetConfig(inputs?.dataset_config, inputs?.dataset_name)

  const navigate = useNavigate()
  const required = inputs.model_name && inputs.dataset_name && ((pushToHF && inputs?.hf_push_repo) || !pushToHF)

  const resetInputs = () => {
    setPushToHF(false)
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

  const handleExperimentsChange = (key: string, value: any) => {
    setInputs({ ...inputs, experiments_params: { ...inputs?.experiments_params, [key]: value } })
    setAlertError("")
  }

  const handlePromptsChange = (key: string, value: any) => {
    setInputs({ ...inputs, prompts_params: { ...inputs?.prompts_params, [key]: value } })
    setAlertError("")
  }

  const handleTrainingChange = (key: string, value: any) => {
    setInputs({ ...inputs, training_params: { ...inputs?.training_params, [key]: value } })
    setAlertError("")
  }

  const handlePushToHFChange = (push: boolean) => {
    if (!push) {
      const { hf_push_repo, ...newInputs } = inputs
      setInputs(newInputs)
    }
    setPushToHF(push)
  }

  const onCheck = (e: React.FormEvent) => {
    e.preventDefault()
    if (Object.entries(errors).length) setAlertError("Please fix the errors before creating the job.")
    else setOpenSubmit(true)
  }

  const onSubmit = async () => {
    try {
      const newJob: Job = await createJobTrain(inputs)
      resetInputs()
      setAlertSuccess(`Successfully created job ${newJob.name} (${newJob.id})`)
      setTimeout(() => navigate(`/jobs`), 2000)
    } catch (error) {
      console.error("Error creating job:", error)
      setAlertError("Error creating job. Please try again.")
    }
  }

  // console.log("input", inputs)
  // console.log("errors", errors)

  return (
    <Container className="fr-my-3w">
      <Button size="sm" variant="tertiary" icon="arrow-left-line" onClick={() => navigate("/jobs")}>
        Back to jobs
      </Button>
      <Title as="h3" className="fr-mb-4w fr-mt-3w">
        New Training Job
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
          label="Training Pipeline"
          selectedKey={inputs.pipeline}
          onSelectionChange={(key) => handleInputsChange("pipeline", key)}
          isRequired
        >
          <SelectOption key={"causallm"}>CausalLM</SelectOption>
          <SelectOption key={"causallm-unsloth"}>CausalLM with Unsloth</SelectOption>
        </Select>
        <SmartTextInput
          value={inputs?.experiments_params?.project || ""}
          onChange={(value) => handleExperimentsChange("project", value)}
          onError={(value) => handleErrorsChange("experiments_project", value)}
          validateSync={validateAplhaNum}
          label="Experiment Project Name"
          hint="Name of the experiment project. Use 'Default' if not set."
          placeholder="entity-extraction-acknowledgments"
        />
        <Toggle
          label="Run job on GPU"
          checked={Boolean(inputs.gpu)}
          onChange={(e) => handleInputsChange("gpu", Number(e.target.checked))}
        />
        <Toggle
          label="Push model on HuggingFace (recommanded)"
          checked={pushToHF}
          onChange={(e) => handlePushToHFChange(e.target.checked)}
        />
        {pushToHF && (
          <Container fluid className="fr-mt-2w">
            <SmartTextInput
              value={inputs.hf_push_repo || ""}
              onChange={(value) => handleInputsChange("hf_push_repo", value)}
              onError={(value) => handleErrorsChange("hf_push_repo", value)}
              validateAsync={(value) => validateRepoName(value, pushToHF, false, "dataesr")}
              label="HuggingFace Name"
              hint="Name of the HuggingFace repository to push the model."
              placeholder="dataesr/my-trained-model"
              required={pushToHF}
            />
          </Container>
        )}
        <Accordion title="Training options" className="fr-mt-5w">
          {inputs?.training_params && (
            <TagGroup>
              {Object.entries(inputs.training_params).map(([key, value]) => (
                <Tag color="blue-cumulus">{`${key}: ${value}`}</Tag>
              ))}
            </TagGroup>
          )}
          <Row>
            <Col md="5">
              <SmartTextInput
                className="fr-pr-2w"
                value={trainingArg?.key || ""}
                onChange={(value) => setTrainingArg({ ...trainingArg, key: String(value).toUpperCase() })}
                onError={(value) => handleErrorsChange("training_arg", value)}
                validateSync={validateAplhaNum}
                label="Training Param Name"
                hint="Name of the training param to add."
                placeholder="num_batch_size"
              />
            </Col>
            <Col md="5">
              <SmartTextInput
                className="fr-pr-2w"
                value={trainingArg?.value || ""}
                onChange={(value) => setTrainingArg({ ...trainingArg, value: value })}
                onError={(value) => handleErrorsChange("training_arg", value)}
                validateSync={validateAplhaNum}
                label="Training Param Value"
                hint="Value of the training param to add."
                placeholder="2"
              />
            </Col>
            <Col md="2">
              <Button
                variant="secondary"
                onClick={() => {
                  handleTrainingChange(trainingArg.key, trainingArg.value)
                  setTrainingArg(null)
                }}
                disabled={!trainingArg?.key || !trainingArg.value}
              >
                Add
              </Button>
            </Col>
          </Row>
        </Accordion>
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
                value={inputs?.prompts_params?.instruction || selectedConfig?.instruction || ""}
                placeholder="You are a helpful assistant..."
                onChange={(e) => handlePromptsChange("instruction", e.target.value)}
                // messageType={errors.dataset_instruction ? "error" : undefined}
                // message={errors.dataset_instruction || undefined}
              />
              <TextInput
                className="fr-mt-2w"
                label="Dataset prompts text format"
                hint="Text format that will be applied to all prompts."
                value={inputs?.prompts_params?.instruction || selectedConfig?.text_format || ""}
                placeholder="### Instruction:\n {instruction}..."
                onChange={(e) => handleInputsChange("text_format", e.target.value)}
                // messageType={errors.dataset_text_format ? "error" : undefined}
                // message={errors.dataset_text_format || undefined}
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
        </Accordion>
        <Accordion title="Experiment options">
          <SmartTextInput
            value={inputs?.experiments_params?.name_tag || ""}
            onChange={(value) => handleExperimentsChange("name_tag", value)}
            onError={(error) => handleErrorsChange("experiments_name_tag", error)}
            validateSync={validateAplhaNum}
            maxLength={12}
            label="Experiment Run Tag"
            hint="Add a tag to the experiment run name"
            placeholder="markdown-v2"
          />
          <Toggle
            label="Disable experiment reporting"
            checked={inputs?.experiments_params?.disabled || false}
            onChange={(e) => handleExperimentsChange("disabled", e.target.checked)}
          />
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
            Create job
          </Button>
        </div>
        <Container fluid>
          <Modal isOpen={openSubmit} hide={() => null}>
            <ModalTitle>Confirm job</ModalTitle>
            <ModalContent>
              <Text>Are you sure you want to submit the following job ?</Text>
              {Object.entries(inputs).map(([key, value]) => (
                <Text className="fr-mb-1v fr-text--legend">{`- ${key}: ${
                  typeof value === "object" ? JSON.stringify(value) : String(value)
                }`}</Text>
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
                  <Button onClick={onSubmit}>Create</Button>
                </div>
              )}
            </ModalFooter>
          </Modal>
        </Container>
      </Container>
    </Container>
  )
}
