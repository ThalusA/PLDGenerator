// noinspection HtmlDeprecatedAttribute

import {Octokit} from 'octokit'
import * as fs from 'node:fs'
import {program} from 'commander'

import {PLDSchema, UserStory} from './pld'
import {LocaleDictionary} from './locale'

function bodyFromUserStory(locale: LocaleDictionary, userStory: UserStory): string {
  const statusMapper: Record<string, string> = {
    'To do': locale.to_do,
    'WIP': locale.wip,
    'Done': locale.done,
    'Abandoned': locale.abandoned,
  }

  return (`<table>
    <tr>
        <td colspan="2" align="center" width="2000x">${userStory.name}</td>
    </tr>
    <tr>
        <td>${locale.as_user}:<br>${userStory.user}</td>
        <td>${locale.user_want}:<br>${userStory.action}</td>
    </tr>
    <tr>
        <td colspan="2">${locale.description}: ${userStory.description}</td>
    </tr>
    <tr>
        <td colspan="2">${locale.definition_of_done}:<br>
            <ul>
                ${userStory.definitions_of_done ? userStory.definitions_of_done.map(definition_of_done => `<li>${definition_of_done}</li>`).join('\n') : '' }
            </ul>
        </td>
    </tr>
    <tr>
        <td colspan="2">${locale.assignation}: ${userStory.assignments ? userStory.assignments.join(", ") : ''}</td>
    </tr>
    <tr>
        <td>${locale.estimated_duration}:</td>
        <td>
            ${userStory.estimated_duration} ${locale.man_days} (${Math.ceil(userStory.estimated_duration * 8)} ${locale.hours})
        </td>
    </tr>
    <tr>
        <td>
            ${locale.status}:
        </td>
        <td>
            ${userStory.status ? statusMapper[userStory.status] : ''}
        </td>
    </tr>
    <tr>
        <td colspan="2">${locale.due_date}: ${userStory.due_date}<br>
    </tr>
    <tr>
        <td colspan="2">${locale.end_date}: ${userStory.end_date}<br>
    </tr>
    ${userStory.comments && userStory.comments.length > 0 ? `
    <tr>
        <td colspan="2">${locale.comments}:${userStory.comments instanceof String ? ` ${userStory.comments}` : ''}<br>
            ${userStory.comments instanceof Array ? `<ul>
                ${userStory.comments.map(comment => `<li>${comment}</li>`).join('\n')}
            </ul>` : '' }
        </td>
    </tr>
    ` : '' }
</table>`)
}

function bodyFromPLD(locale: LocaleDictionary, pld: PLDSchema): string {
  return (`# ${locale.document_description}

<table>
    <tr>
        <th>${locale.title}</th>
        <td>${pld.title}</td>
    </tr>
    <tr>
        <th>${locale.subtitle}</th>
        <td>${pld.subtitle ?? ''}</td>
    </tr>
    <tr>
        <th>${locale.description}</th>
        <td>${pld.description ?? ''}</td>
    </tr>
    <tr>
        <th>${locale.locale}</th>
        <td>${pld.locale}</td>
    </tr>
    <tr>
        <th>${locale.authors}</th>
        <td>${pld.authors ? pld.authors.join(', ') : ''}</td>
    </tr>
    <tr>
        <th>${locale.updated_date}</th>
        <td>${pld.versions ? (pld.versions.at(-1)?.date ?? '') : ''}</td>
    </tr>
    <tr>
        <th>${locale.model_version}</th>
        <td>${pld.versions ? (pld.versions.at(-1)?.version ?? '') : ''}</td>
    </tr>
</table>

# ${locale.revision_table}

<table>
    <thead>
        <tr>
            <th>${locale.date}</th>
            <th>${locale.version}</th>
            <th>${locale.authors}</th>
            <th>${locale.sections}</th>
            <th>${locale.comment}</th>
        </tr>
    </thead>
    <tbody>
        ${pld.versions ? pld.versions.map(version => `<tr>
            <td>${version.date}</td>
            <td>${version.version}</td>
            <td>${version.authors ? version.authors.join(', ') : ''}</td>
            <td>${version.sections}</td>
            <td>${version.comment}</td>
        </tr>`).join('\n') : ''}
    </tbody>
</table>`)
}

function checkIfIssueNumberInBody(issueNumber: number, body?: string): boolean {
  if (body === undefined) {
    return false
  }

  return body.includes(`- [x] #${issueNumber}`)
}

interface Options {
  token: string
  owner: string
  repo: string
}

enum labels {
  UserStory = 'user-story',
  Deliverable = 'deliverable',
  Subset = 'subset',
  PLD = 'pld',
}

type Issue = Awaited<ReturnType<Octokit['rest']['issues']['listForRepo']>>['data'][0]
type CreatedIssue = Awaited<ReturnType<Octokit['rest']['issues']['create']>>['data']


interface SubsetTree extends Object {
  [key: number]: Issue;
}

interface DeliverableTree extends Object {
  0?: Issue;
  [key: number]: SubsetTree | undefined;

}

interface PLDTree extends Object {
  0?: Issue;
  [key: number]: DeliverableTree | undefined;
}


program
  .enablePositionalOptions()

program
  .option('-t, --token <token>', 'GitHub Token')
  .option('-o, --owner <owner>', 'GitHub Owner')
  .option('-r, --repo <repo>', 'GitHub Repo')
  .version('0.0.1')


program
  .command('export <filepath>')
  .description('Export PLD as a JSON file to <filepath> from GitHub Issues')
  .passThroughOptions()
  .action(async (filepath: string) => {
    const options: Options = program.opts()

    const octokit = new Octokit({auth: options.token})
    const issueIterator = octokit.paginate.iterator(octokit.rest.issues.listForRepo, {
      owner: options.owner,
      repo: options.repo,
      per_page: 100,
    })
    const availableIssues: PLDTree = {}
    for await (const {data: issues} of issueIterator) {
      for (const issue of issues) {
        // @ts-ignore
        if (issue.labels.find(label => label.name === labels.PLD)) {
          availableIssues[0] = issue
        // @ts-ignore
        } else if (issue.labels.find(label => label.name === labels.Deliverable)) {
          const [deliverable] = issue.title.split(' ')[0].split('.').map(str => Number(str))
          if (availableIssues[deliverable] === undefined) {
            availableIssues[deliverable] = {}
          }
          // @ts-ignore
          availableIssues[deliverable][0] = issue
        // @ts-ignore
        } else if (issue.labels.find(label => label.name === labels.Subset)) {
          const [deliverable, subset] = issue.title.split(' ')[0].split('.').map(str => Number(str))
          if (availableIssues[deliverable] === undefined) {
            availableIssues[deliverable] = {}
          }
          // @ts-ignore
          if (availableIssues[deliverable][subset] === undefined) {
            // @ts-ignore
            availableIssues[deliverable][subset] = {}
          }
          // @ts-ignore
          availableIssues[deliverable][subset][0] = issue
        // @ts-ignore
        } else if (issue.labels.find(label => label.name === labels.UserStory)) {
          const [deliverable, subset, userStory] = issue.title.split(' ')[0].split('.').map(str => Number(str))
          if (availableIssues[deliverable] === undefined) {
            availableIssues[deliverable] = {}
          }
          // @ts-ignore
          if (availableIssues[deliverable][subset] === undefined) {
            // @ts-ignore
            availableIssues[deliverable][subset] = {}
          }
          // @ts-ignore
          availableIssues[deliverable][subset][userStory] = issue
        }
      }
    }
  })

program
  .command('import <filepath>')
  .description('Import PLD from a JSON file located at <filepath> to GitHub Issues')
  .passThroughOptions()
  .action(async (filepath: string) => {
    const options: Options = program.opts()

    const octokit = new Octokit({auth: options.token})

    const pld: PLDSchema = JSON.parse(fs.readFileSync(filepath, 'utf8'))
    const locale: LocaleDictionary = JSON.parse(fs.readFileSync(`../src/locale/${pld.locale}.json`, 'utf8'))

    const labelPromises = []
    for (const label of Object.values(labels)) {
      labelPromises.push(octokit.rest.issues.getLabel({
        owner: options.owner,
        repo: options.repo,
        name: label,
      }).catch(() => octokit.rest.issues.createLabel({
        owner: options.owner,
        repo: options.repo,
        name: label,
      })))
    }

    await Promise.all(labelPromises)

    const availableIssues: Record<string, Issue | CreatedIssue> = {}
    const issueIterator = octokit.paginate.iterator(octokit.rest.issues.listForRepo, {
      owner: options.owner,
      repo: options.repo,
      per_page: 100,
    })
    for await (const {data: issues} of issueIterator) {
      for (const issue of issues) {
        availableIssues[issue.title.split(' ', 2)[0]] = issue
      }
    }

    const savedPLD = availableIssues[pld.title] ?? await octokit.rest.issues.create({
      owner: options.owner,
      repo: options.repo,
      title: pld.title,
      labels: [labels.PLD],
      body: bodyFromPLD(locale, pld),
    }).then(response => response.data)
    const deliverables = []
    if (pld.deliverables) {
      let deliverableDepth = 1
      for (const deliverable of pld.deliverables) {
        const savedDeliverable = availableIssues[`${deliverableDepth}`] ?? await octokit.rest.issues.create({
          owner: options.owner,
          repo: options.repo,
          title: `${deliverableDepth} ${deliverable.name}`,
          labels: [labels.Deliverable],
          body: deliverable.description,
        }).then(response => response.data)
        deliverables.push(savedDeliverable)
        const subsets = []

        if (deliverable.subsets) {
          let subsetDepth = 1
          for (const subset of deliverable.subsets) {
            const savedSubset = availableIssues[`${deliverableDepth}.${subsetDepth}`] ?? await octokit.rest.issues.create({
              owner: options.owner,
              repo: options.repo,
              title: `${deliverableDepth}.${subsetDepth} ${subset.name}`,
              labels: [labels.Subset],
              body: subset.description,
            }).then(response => response.data)
            subsets.push(savedSubset)
            const user_stories = []
            if (subset.user_stories) {
              let userStoryDepth = 1
              for (const userStory of subset.user_stories) {
                const savedUserStory = availableIssues[`${deliverableDepth}.${subsetDepth}.${userStoryDepth}`] ?? await octokit.rest.issues.create({
                  owner: options.owner,
                  repo: options.repo,
                  title: `${deliverableDepth}.${subsetDepth}.${userStoryDepth} ${userStory.name}`,
                  labels: [labels.UserStory],
                  body: bodyFromUserStory(locale, userStory),
                }).then(response => response.data)
                user_stories.push(savedUserStory)
                await octokit.rest.issues.update({
                  owner: options.owner,
                  repo: options.repo,
                  issue_number: savedUserStory.number,
                  title: `${deliverableDepth}.${subsetDepth}.${userStoryDepth} ${userStory.name}`,
                  labels: [labels.UserStory],
                  body: bodyFromUserStory(locale, userStory),
                })
                userStoryDepth += 1
              }
            }

            await octokit.rest.issues.update({
              owner: options.owner,
              repo: options.repo,
              issue_number: savedSubset.number,
              title: `${deliverableDepth}.${subsetDepth} ${subset.name}`,
              labels: [labels.Subset],
              body: subset.description ? '# Description\n\n' + subset.description + '\n\n# Linked issues\n' + user_stories.map(userStory => `\n- [${checkIfIssueNumberInBody(userStory.number, savedSubset.body_text) ? 'x' : ' '}] #${userStory.number}`).join('') : undefined,
            })

            subsetDepth += 1
          }
        }

        await octokit.rest.issues.update({
          owner: options.owner,
          repo: options.repo,
          issue_number: savedDeliverable.number,
          title: `${deliverableDepth} ${deliverable.name}`,
          labels: [labels.Deliverable],
          body: deliverable.description ? '# Description\n\n' + deliverable.description + '\n\n# Linked issues\n' + subsets.map(subset => `\n- [${checkIfIssueNumberInBody(subset.number, savedDeliverable.body_text) ? 'x' : ' '}] #${subset.number}`).join('') : undefined,
        })

        deliverableDepth += 1
      }
    }

    await octokit.rest.issues.update({
      owner: options.owner,
      repo: options.repo,
      issue_number: savedPLD.number,
      title: `${savedPLD.title}`,
      labels: [labels.PLD],
      body: pld.description ? '# Description\n\n' + bodyFromPLD(locale, pld) + '\n\n# Linked issues' + deliverables.map(deliverable => `\n- [${checkIfIssueNumberInBody(deliverable.number, savedPLD.body_text) ? 'x' : ' '}] #${deliverable.number}`).join('') : undefined,
    })
  })

program.parse()
