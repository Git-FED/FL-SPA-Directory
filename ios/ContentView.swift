import SwiftUI

/**
 * Main screen: search, status filter, tier switch, list, detail sheet,
 * subscriber unlock. Dark brand palette via tokens set inline (matches
 * web/css/style.css exactly).
 */

// MARK: - Design tokens (single source for the iOS surface)
enum Palette {
    static let bg = Color(red: 0x0B / 255, green: 0x0E / 255, blue: 0x14 / 255)
    static let bgRaised = Color(red: 0x13 / 255, green: 0x18 / 255, blue: 0x24 / 255)
    static let bgInset = Color(red: 0x0D / 255, green: 0x11 / 255, blue: 0x17 / 255)
    static let border = Color(red: 0x26 / 255, green: 0x30 / 255, blue: 0x42 / 255)
    static let text = Color(red: 0xE6 / 255, green: 0xE9 / 255, blue: 0xEF / 255)
    static let textMuted = Color(red: 0x9A / 255, green: 0xA4 / 255, blue: 0xB5 / 255)
    static let textFaint = Color(red: 0x6B / 255, green: 0x76 / 255, blue: 0x87 / 255)
    static let accent = Color(red: 0x2D / 255, green: 0xD4 / 255, blue: 0xA7 / 255)
    static let danger = Color(red: 0xFF / 255, green: 0x5F / 255, blue: 0x6D / 255)
    static let warning = Color(red: 0xF2 / 255, green: 0xC1 / 255, blue: 0x4E / 255)
}

// MARK: - Root view

struct ContentView: View {
    @EnvironmentObject var data: DataManager

    @State private var query = ""
    @State private var statusFilter = "All statuses"
    @State private var tier: Tier = .licensed
    @State private var codeInput = ""
    @State private var showSettings = false

    enum Tier: String, CaseIterable, Identifiable {
        case licensed = "Licensed"
        case unlicensed = "Unlicensed watchlist"
        var id: String { rawValue }
    }

    private let statuses = ["All statuses", "Clear", "Active", "Delinquent", "Expired", "Inactive", "Probation"]

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // brand + data chips
                header

                // tier tabs
                Picker("Tier", selection: $tier) {
                    ForEach(Tier.allCases) { t in
                        Text(t.rawValue).tag(t)
                    }
                }
                .pickerStyle(.segmented)
                .padding(.horizontal)
                .padding(.top, 8)

                // search + filter
                searchRow

                // unlock row (subscriber tier locked)
                if tier == .unlicensed && !data.unlocked {
                    unlockRow
                }

                if tier == .unlicensed && data.unlocked {
                    HStack {
                        Button("Lock watchlist") { data.lock() }
                            .foregroundColor(Palette.danger)
                        Spacer()
                    }
                    .padding(.horizontal)
                    .padding(.bottom, 6)
                }

                // list
                List {
                    if tier == .licensed {
                        ForEach(data.searchLicensed(query, status: statusFilter == "All statuses" ? nil : statusFilter)) { p in
                            NavigationLink {
                                ParlorDetail(parlor: p)
                            } label: {
                                LicensedRow(p)
                            }
                            .listRowBackground(Palette.bgRaised)
                        }
                    } else {
                        ForEach(data.searchUnlicensed(query, status: statusFilter == "All statuses" ? nil : statusFilter)) { p in
                            NavigationLink {
                                UnlicensedDetail(parlor: p)
                            } label: {
                                UnlicensedRow(p)
                            }
                            .listRowBackground(Palette.bgRaised)
                        }
                    }
                }
                .listStyle(.plain)
                .background(Palette.bg)

                if tier == .unlicensed && !data.unlocked && data.unlicensed.isEmpty {
                    Spacer()
                    Text("Watchlist is locked. Enter your subscriber code.")
                        .foregroundColor(Palette.textFaint)
                    Spacer()
                }
            }
            .background(Palette.bg)
            .navigationTitle("FED-SPA")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        showSettings = true
                    } label: {
                        Image(systemName: "gearshape")
                    }
                }
            }
            .sheet(isPresented: $showSettings) {
                SettingsView()
                    .environmentObject(data)
            }
        }
        .preferredColorScheme(.dark)
    }

    // ------------------------------------------------------------------
    // pieces
    // ------------------------------------------------------------------
    private var header: some View {
        HStack {
            VStack(alignment: .leading, spacing: 2) {
                Text("Florida Establishment Directory")
                    .font(.caption)
                    .foregroundColor(Palette.textMuted)
                Text("Data as of \(data.asOf)")
                    .font(.caption2)
                    .foregroundColor(Palette.textFaint)
            }
            Spacer()
            Text("\(currentCount) listed")
                .font(.caption)
                .foregroundColor(Palette.accent)
        }
        .padding()
        .background(Palette.bgRaised)
    }

    private var searchRow: some View {
        HStack(spacing: 8) {
            TextField("Search name, license, city…", text: $query)
                .textFieldStyle(.roundedBorder)
            Menu {
                ForEach(statuses, id: \.self) { s in
                    Button(s) { statusFilter = s }
                }
            } label: {
                Text(statusFilter)
                    .font(.caption)
                    .foregroundColor(Palette.accent)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 6)
                    .background(Palette.bgInset)
                    .cornerRadius(8)
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }

    private var unlockRow: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                SecureField("Subscriber code", text: $codeInput)
                    .textFieldStyle(.roundedBorder)
                Button("Unlock") {
                    data.unlock(code: codeInput)
                    codeInput = ""
                }
                .buttonStyle(.borderedProminent)
                .tint(Palette.accent)
            }
            if let err = data.unlockError {
                Text(err).font(.caption).foregroundColor(Palette.danger)
            }
        }
        .padding(.horizontal)
        .padding(.bottom, 8)
    }

    private var currentCount: Int {
        tier == .licensed
            ? data.searchLicensed(query, status: statusFilter == "All statuses" ? nil : statusFilter).count
            : (data.unlocked ? data.searchUnlicensed(query, status: statusFilter == "All statuses" ? nil : statusFilter).count : 0)
    }
}

// MARK: - Rows

struct LicensedRow: View {
    let p: LicensedParlor

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(p.businessName)
                    .font(.body.weight(.semibold))
                    .foregroundColor(Palette.text)
                Spacer()
                StatusBadge(text: p.status.capitalized)
            }
            Text("License \(p.licenseNumber)")
                .font(.caption)
                .foregroundColor(Palette.textMuted)
            Text("\(p.address.city), \(p.address.state)")
                .font(.caption)
                .foregroundColor(Palette.textMuted)
        }
        .padding(.vertical, 4)
    }
}

struct UnlicensedRow: View {
    let p: UnlicensedParlor

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Text(p.businessName)
                    .font(.body.weight(.semibold))
                    .foregroundColor(Palette.text)
                Spacer()
                StatusBadge(text: p.status.replacingOccurrences(of: "_", with: " ").capitalized)
            }
            Text("\(p.address.city), \(p.address.state)")
                .font(.caption)
                .foregroundColor(Palette.textMuted)
        }
        .padding(.vertical, 4)
    }
}

struct StatusBadge: View {
    let text: String

    var body: some View {
        Text(text)
            .font(.caption2.weight(.bold))
            .foregroundColor(Color(red: 0x06 / 255, green: 0x25 / 255, blue: 0x1B / 255))
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(DataManager.statusColor(text))
            .cornerRadius(6)
    }
}

// MARK: - Details

struct ParlorDetail: View {
    let parlor: LicensedParlor

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text(parlor.businessName)
                    .font(.title2.weight(.bold))
                    .foregroundColor(Palette.text)
                StatusBadge(text: parlor.status.capitalized)

                Grid(alignment: .leading, horizontalSpacing: 14, verticalSpacing: 7) {
                    GridRow {
                        Text("License").foregroundColor(Palette.textFaint)
                        Text(parlor.licenseNumber).foregroundColor(Palette.text)
                    }
                    GridRow {
                        Text("Profession").foregroundColor(Palette.textFaint)
                        Text(parlor.profession).foregroundColor(Palette.text)
                    }
                    GridRow {
                        Text("Expires").foregroundColor(Palette.textFaint)
                        Text(parlor.expirationDate).foregroundColor(Palette.text)
                    }
                    GridRow {
                        Text("Issued").foregroundColor(Palette.textFaint)
                        Text(parlor.originalIssueDate).foregroundColor(Palette.text)
                    }
                    GridRow {
                        Text("Address").foregroundColor(Palette.textFaint)
                        Text("\(parlor.address.street), \(parlor.address.city), \(parlor.address.state) \(parlor.address.zip)")
                            .foregroundColor(Palette.text)
                    }
                    GridRow {
                        Text("County").foregroundColor(Palette.textFaint)
                        Text(parlor.county).foregroundColor(Palette.text)
                    }
                    GridRow {
                        Text("Discipline on file").foregroundColor(Palette.textFaint)
                        Text(parlor.disciplineOnFile ? "YES" : "No")
                            .foregroundColor(parlor.disciplineOnFile ? Palette.danger : Palette.text)
                    }
                    GridRow {
                        Text("Public complaint").foregroundColor(Palette.textFaint)
                        Text(parlor.publicComplaint ? "YES" : "No")
                            .foregroundColor(parlor.publicComplaint ? Palette.danger : Palette.text)
                    }
                    GridRow {
                        Text("Data as of").foregroundColor(Palette.textFaint)
                        Text(parlor.dataAsOf).foregroundColor(Palette.text)
                    }
                }
                .font(.callout)

                if let notes = parlor.notes, !notes.isEmpty {
                    Text(notes)
                        .font(.footnote)
                        .foregroundColor(Palette.textMuted)
                }
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .background(Palette.bg)
        .navigationTitle("Establishment")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct UnlicensedDetail: View {
    let parlor: UnlicensedParlor

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text(parlor.businessName)
                    .font(.title2.weight(.bold))
                    .foregroundColor(Palette.text)
                StatusBadge(text: parlor.status.replacingOccurrences(of: "_", with: " ").capitalized)

                Grid(alignment: .leading, horizontalSpacing: 14, verticalSpacing: 7) {
                    GridRow {
                        Text("Address").foregroundColor(Palette.textFaint)
                        Text("\(parlor.address.street), \(parlor.address.city), \(parlor.address.state) \(parlor.address.zip)")
                            .foregroundColor(Palette.text)
                    }
                    GridRow {
                        Text("County").foregroundColor(Palette.textFaint)
                        Text(parlor.county).foregroundColor(Palette.text)
                    }
                    GridRow {
                        Text("Last checked").foregroundColor(Palette.textFaint)
                        Text(parlor.lastChecked).foregroundColor(Palette.text)
                    }
                    GridRow {
                        Text("Reason").foregroundColor(Palette.textFaint)
                        Text(parlor.reason).foregroundColor(Palette.danger)
                    }
                }
                .font(.callout)
            }
            .padding()
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .background(Palette.bg)
        .navigationTitle("Unlicensed")
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Settings

struct SettingsView: View {
    @EnvironmentObject var data: DataManager
    @Environment(\.dismiss) private var dismiss

    @State private var codeInput = ""

    var body: some View {
        NavigationView {
            Form {
                Section("Subscriber code") {
                    Toggle("Remember my code", isOn: Binding(
                        get: { data.rememberCode },
                        set: { data.setRemember($0) }
                    ))
                    if data.rememberCode {
                        SecureField("Subscriber code", text: $codeInput)
                        Button("Save code") {
                            UserDefaults.standard.set(codeInput, forKey: data.savedCodeKey)
                            codeInput = ""
                        }
                        Button("Clear stored code", role: .destructive) {
                            data.setRemember(false)
                        }
                    }
                }
                Section("About data") {
                    LabeledContent("Version", value: "v\(data.version)")
                    LabeledContent("Data as of", value: data.asOf)
                    LabeledContent("Licensed", value: "\(data.licensed.count)")
                    LabeledContent("Update frequency", value: "Annual")
                }
                Section {
                    Text("The stored code lives in UserDefaults on this device only. Nothing is ever transmitted - FED-SPA has no backend.")
                        .font(.footnote)
                        .foregroundColor(Palette.textMuted)
                }
            }
            .navigationTitle("Settings")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }
}

#if DEBUG
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView().environmentObject(DataManager())
    }
}
#endif
