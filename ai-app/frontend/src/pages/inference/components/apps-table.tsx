import { Table } from "@codegouvfr/react-dsfr/Table"
import CopyToClipboard from "../../../components/copy-to-clipboard"
import { Button, Tag, Text } from "@dataesr/dsfr-plus"
import { InferenceApp } from "../../../api/inference/types"
import { getStateColor } from "../helpers/colors"

const TABLE_CONFIG = [
  { header: "Name / ID", component: "name" },
  { header: "Status", component: "status" },
  { header: "Resources", component: "resources" },
  { header: "Actions", component: "actions" },
]

const buildTableComponents = (app: InferenceApp) => {
  const name = (
    <>
      <CopyToClipboard copyText={app.spec.name}>
        <Text size="sm" bold>
          {app.spec.name}
        </Text>
      </CopyToClipboard>
      <CopyToClipboard copyText={app.id}>
        <Text className="fr-text-mention--grey" size="sm">
          {app.id}
        </Text>
      </CopyToClipboard>
    </>
  )
  const status = <Tag color={getStateColor(app.status.state)}>{app.status.state}</Tag>
  const resources = app.spec.resources.gpu ? (
    <>
      <Text size="sm">GPU: {app.spec.resources.gpu}</Text>
      <Text size="sm">{app.spec.resources.gpuModel}</Text>
    </>
  ) : (
    <Text size="sm">CPU: {app.spec.resources.cpu}</Text>
  )

  const actions = (
    <Button icon="external-link-line" size="sm" variant="text" onClick={() => window.open(app.external_url, "_blank")}>
      Open
    </Button>
  )

  return {
    name,
    status,
    resources,
    actions,
  }
}

export default function InferenceAppsTable({ apps }: { apps: InferenceApp[] }) {
  const headers = TABLE_CONFIG.map((col) => col.header)
  const data = apps.map((app) => buildTableComponents(app)).map((app) => TABLE_CONFIG.map((col) => app[col.component]))
  return <Table className="fr-pt-0" headers={headers} data={data} />
}
