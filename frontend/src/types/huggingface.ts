import * as hub from "@huggingface/hub"

type HuggingFaceAdditionalInfos = {
  config: { architectures: Array<string>; model_type: string }
  tags: string[]
}
export type HuggingFaceModel = hub.ModelEntry & HuggingFaceAdditionalInfos
export type HuggingFaceModels = Array<HuggingFaceModel>
