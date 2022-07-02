package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path"
	"sort"
	"strings"
	"time"

	"github.com/rs/zerolog"
)

const (
	DATA_PATH = "../data"
)

func main() {
	p := New()
	languages, err := p.initLanguageDataset(DATA_PATH)
	if err != nil {
		panic(err)
	}

	languageList := p.sortLanguageDataset(languages)

	markdownSections := make([]string, len(languageList))
	for _, language := range languageList {
		markdownSections = append(markdownSections, p.createLanaguageMDSection(language, languages[language]))
	}

	fileBytes := []byte(p.createTableOfContents(languageList))
	for _, section := range markdownSections {
		fileBytes = append(fileBytes, []byte(section)...)
	}

	if err := p.writeMDSectionsToREADME(path.Join("../", "README.md"), fileBytes); err != nil {
		p.log.Err(err).Msg("failed to write to file")
	}

	return
}

//
// Data Parser
//

type Parser struct {
	log zerolog.Logger
}

func New() *Parser {
	return &Parser{
		log: zerolog.New(os.Stdout).
			With().
			Timestamp().
			Logger(),
	}
}

func (s *Parser) sortLanguageDataset(dataset map[string][]Items) []string {
	sorted := make([]string, 0, len(dataset))
	for language := range dataset {
		sorted = append(sorted, language)
	}

	sort.Sort(sort.StringSlice(sorted))

	return sorted
}

func (s *Parser) initLanguageDataset(p string) (map[string][]Items, error) {
	dir, err := os.ReadDir(p)
	if err != nil {
		s.log.Err(err).Msg("failed to load directory contents from " + DATA_PATH)
		return nil, err
	}

	var languages = make(map[string][]Items, 0)

	// populate the array with each language we parse
	for _, f := range dir {
		language := s.deriveLanguageFromPath(f.Name())
		languages[language] = append(languages[language], s.retrieveLanguageItemsFromPath(f.Name())...)
	}

	return languages, nil
}

func (s *Parser) deriveLanguageFromPath(p string) string {
	return strings.Split(p, "-")[2]
}

func (s *Parser) retrieveLanguageItemsFromPath(p string) []Items {
	data, err := os.ReadFile(path.Join(DATA_PATH, p))
	if err != nil {
		s.log.Err(err).Msg("failed to read file")
		return nil
	}

	var response Response // json data will be unmarshalled into

	if err := json.Unmarshal(data, &response); err != nil {
		s.log.Err(err).Msg("failed to unmarshall data for dataset: " + p)
		return nil
	}

	return response.Items
}

func (s *Parser) createTableOfContents(languages []string) string {
	content := `# awesome-blazingly-fast
A (satire) awesome list which lists all projects which are described as 'blazingly fast'
	
--- 
	
## Blazingly Fast Repositories By Language

`

	for _, language := range languages {
		content += fmt.Sprintf("- [%s](#%s)\n", language, language)
	}

	return content
}

func (s *Parser) createLanaguageMDSection(language string, items []Items) string {
	title := fmt.Sprintf("\n## %s\n", language)

	content := ""

	for _, item := range items {
		content += fmt.Sprintf("\n- [%s](%s) - %s", item.Name, item.HTMLURL, item.Description)
	}

	return title + content + "\n"
}

func (s *Parser) writeMDSectionsToREADME(file string, sections []byte) error {
	return os.WriteFile(file, sections, os.ModeAppend)
}

//
// Data Models
//

type Response struct {
	TotalCount        int     `json:"total_count,omitempty"`
	IncompleteResults bool    `json:"incomplete_results,omitempty"`
	Items             []Items `json:"items,omitempty"`
}
type Owner struct {
	Login             string `json:"login,omitempty"`
	ID                int    `json:"id,omitempty"`
	NodeID            string `json:"node_id,omitempty"`
	AvatarURL         string `json:"avatar_url,omitempty"`
	GravatarID        string `json:"gravatar_id,omitempty"`
	URL               string `json:"url,omitempty"`
	HTMLURL           string `json:"html_url,omitempty"`
	FollowersURL      string `json:"followers_url,omitempty"`
	FollowingURL      string `json:"following_url,omitempty"`
	GistsURL          string `json:"gists_url,omitempty"`
	StarredURL        string `json:"starred_url,omitempty"`
	SubscriptionsURL  string `json:"subscriptions_url,omitempty"`
	OrganizationsURL  string `json:"organizations_url,omitempty"`
	ReposURL          string `json:"repos_url,omitempty"`
	EventsURL         string `json:"events_url,omitempty"`
	ReceivedEventsURL string `json:"received_events_url,omitempty"`
	Type              string `json:"type,omitempty"`
	SiteAdmin         bool   `json:"site_admin,omitempty"`
}
type License struct {
	Key    string `json:"key,omitempty"`
	Name   string `json:"name,omitempty"`
	SpdxID string `json:"spdx_id,omitempty"`
	URL    string `json:"url,omitempty"`
	NodeID string `json:"node_id,omitempty"`
}
type Permissions struct {
	Admin    bool `json:"admin,omitempty"`
	Maintain bool `json:"maintain,omitempty"`
	Push     bool `json:"push,omitempty"`
	Triage   bool `json:"triage,omitempty"`
	Pull     bool `json:"pull,omitempty"`
}
type Items struct {
	ID               int           `json:"id,omitempty"`
	NodeID           string        `json:"node_id,omitempty"`
	Name             string        `json:"name,omitempty"`
	FullName         string        `json:"full_name,omitempty"`
	Private          bool          `json:"private,omitempty"`
	Owner            Owner         `json:"owner,omitempty"`
	HTMLURL          string        `json:"html_url,omitempty"`
	Description      string        `json:"description,omitempty"`
	Fork             bool          `json:"fork,omitempty"`
	URL              string        `json:"url,omitempty"`
	ForksURL         string        `json:"forks_url,omitempty"`
	KeysURL          string        `json:"keys_url,omitempty"`
	CollaboratorsURL string        `json:"collaborators_url,omitempty"`
	TeamsURL         string        `json:"teams_url,omitempty"`
	HooksURL         string        `json:"hooks_url,omitempty"`
	IssueEventsURL   string        `json:"issue_events_url,omitempty"`
	EventsURL        string        `json:"events_url,omitempty"`
	AssigneesURL     string        `json:"assignees_url,omitempty"`
	BranchesURL      string        `json:"branches_url,omitempty"`
	TagsURL          string        `json:"tags_url,omitempty"`
	BlobsURL         string        `json:"blobs_url,omitempty"`
	GitTagsURL       string        `json:"git_tags_url,omitempty"`
	GitRefsURL       string        `json:"git_refs_url,omitempty"`
	TreesURL         string        `json:"trees_url,omitempty"`
	StatusesURL      string        `json:"statuses_url,omitempty"`
	LanguagesURL     string        `json:"languages_url,omitempty"`
	StargazersURL    string        `json:"stargazers_url,omitempty"`
	ContributorsURL  string        `json:"contributors_url,omitempty"`
	SubscribersURL   string        `json:"subscribers_url,omitempty"`
	SubscriptionURL  string        `json:"subscription_url,omitempty"`
	CommitsURL       string        `json:"commits_url,omitempty"`
	GitCommitsURL    string        `json:"git_commits_url,omitempty"`
	CommentsURL      string        `json:"comments_url,omitempty"`
	IssueCommentURL  string        `json:"issue_comment_url,omitempty"`
	ContentsURL      string        `json:"contents_url,omitempty"`
	CompareURL       string        `json:"compare_url,omitempty"`
	MergesURL        string        `json:"merges_url,omitempty"`
	ArchiveURL       string        `json:"archive_url,omitempty"`
	DownloadsURL     string        `json:"downloads_url,omitempty"`
	IssuesURL        string        `json:"issues_url,omitempty"`
	PullsURL         string        `json:"pulls_url,omitempty"`
	MilestonesURL    string        `json:"milestones_url,omitempty"`
	NotificationsURL string        `json:"notifications_url,omitempty"`
	LabelsURL        string        `json:"labels_url,omitempty"`
	ReleasesURL      string        `json:"releases_url,omitempty"`
	DeploymentsURL   string        `json:"deployments_url,omitempty"`
	CreatedAt        time.Time     `json:"created_at,omitempty"`
	UpdatedAt        time.Time     `json:"updated_at,omitempty"`
	PushedAt         time.Time     `json:"pushed_at,omitempty"`
	GitURL           string        `json:"git_url,omitempty"`
	SSHURL           string        `json:"ssh_url,omitempty"`
	CloneURL         string        `json:"clone_url,omitempty"`
	SvnURL           string        `json:"svn_url,omitempty"`
	Homepage         interface{}   `json:"homepage,omitempty"`
	Size             int           `json:"size,omitempty"`
	StargazersCount  int           `json:"stargazers_count,omitempty"`
	WatchersCount    int           `json:"watchers_count,omitempty"`
	Language         string        `json:"language,omitempty"`
	HasIssues        bool          `json:"has_issues,omitempty"`
	HasProjects      bool          `json:"has_projects,omitempty"`
	HasDownloads     bool          `json:"has_downloads,omitempty"`
	HasWiki          bool          `json:"has_wiki,omitempty"`
	HasPages         bool          `json:"has_pages,omitempty"`
	ForksCount       int           `json:"forks_count,omitempty"`
	MirrorURL        interface{}   `json:"mirror_url,omitempty"`
	Archived         bool          `json:"archived,omitempty"`
	Disabled         bool          `json:"disabled,omitempty"`
	OpenIssuesCount  int           `json:"open_issues_count,omitempty"`
	License          License       `json:"license,omitempty"`
	AllowForking     bool          `json:"allow_forking,omitempty"`
	IsTemplate       bool          `json:"is_template,omitempty"`
	Topics           []interface{} `json:"topics,omitempty"`
	Visibility       string        `json:"visibility,omitempty"`
	Forks            int           `json:"forks,omitempty"`
	OpenIssues       int           `json:"open_issues,omitempty"`
	Watchers         int           `json:"watchers,omitempty"`
	DefaultBranch    string        `json:"default_branch,omitempty"`
	Permissions      Permissions   `json:"permissions,omitempty"`
	Score            float64       `json:"score,omitempty"`
}
