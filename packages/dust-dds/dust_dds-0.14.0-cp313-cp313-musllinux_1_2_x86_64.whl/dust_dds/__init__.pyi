from typing import Any 

ANY_SAMPLE_STATE : SampleStateKind= ...
ANY_VIEW_STATE : ViewStateKind = ...
ANY_INSTANCE_STATE : InstanceStateKind= ...
NOT_ALIVE_INSTANCE_STATE : InstanceStateKind= ...
DEFAULT_RELIABILITY_QOS_POLICY_DATA_READER_AND_TOPICS : ReliabilityQosPolicy = ...
DEFAULT_RELIABILITY_QOS_POLICY_DATA_WRITER : ReliabilityQosPolicy = ...

class DomainParticipant:
	r"""
 The [`DomainParticipant`] represents the participation of the application on a communication plane that isolates applications running on the
 same set of physical computers from each other. A domain establishes a *virtual network* linking all applications that
 share the same domain_id and isolating them from applications running on different domains. In this way, several
 independent distributed applications can coexist in the same physical network without interfering, or even being aware
 of each other.

 The [`DomainParticipant`] object plays several roles:
 - It acts as a container for all other Entity objects
 - It acts as factory for the [`Publisher`], [`Subscriber`] and [`Topic`] Entity objects
 - It provides administration services in the domain, offering operations that allow the application to 'ignore' locally any
   information about a given participant ([`DomainParticipant::ignore_participant()`]), publication ([`DomainParticipant::ignore_publication()`]), subscription
   ([`DomainParticipant::ignore_subscription()`]), or topic ([`DomainParticipant::ignore_topic()`]).

 The following operations may be called even if the [`DomainParticipant`] is not enabled. Other operations will return a NotEnabled error if called on a disabled [`DomainParticipant`]:
 - Operations defined at the base-class level namely, [`DomainParticipant::set_qos()`], [`DomainParticipant::get_qos()`], [`DomainParticipant::set_listener()`], and [`DomainParticipant::enable()`].
 - Factory methods: [`DomainParticipant::create_topic()`], [`DomainParticipant::create_publisher()`], [`DomainParticipant::create_subscriber()`], [`DomainParticipant::delete_topic()`], [`DomainParticipant::delete_publisher()`],
   [`DomainParticipant::delete_subscriber()`]
 - Operations that access the status: [`DomainParticipant::get_statuscondition()`]
	"""
	def get_type(type_name: str) -> Any | None  :
		...

	def create_publisher(self, qos: PublisherQos | None  = None, a_listener: Any | None  = None, mask: list[StatusKind] = []) -> Publisher :
		r"""
 This operation creates a [`Publisher`] with the desired QoS policies and attaches to it the specified [`PublisherListener`].
 If the specified QoS policies are not consistent, the operation will fail and no [`Publisher`] will be created.
 The value [`QosKind::Default`] can be used to indicate that the Publisher should be created with the default
 Publisher QoS set in the factory. The use of this value is equivalent to the application obtaining the default Publisher QoS by
 means of the operation [`DomainParticipant::get_default_publisher_qos()`] and using the resulting QoS to create the [`Publisher`].
 The created [`Publisher`] belongs to the [`DomainParticipant`] that is its factory.
 In case of failure, the operation will return an error and no [`Publisher`] will be created.
		"""
		...

	def delete_publisher(self, a_publisher: Publisher) -> None :
		r"""
 This operation deletes an existing [`Publisher`].
 A [`Publisher`] cannot be deleted if it has any attached [`DataWriter`](crate::publication::data_writer::DataWriter) objects. If [`DomainParticipant::delete_publisher()`]
 is called on a [`Publisher`] with existing [`DataWriter`](crate::publication::data_writer::DataWriter) objects, it will return a
 [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError) error.
 The [`DomainParticipant::delete_publisher()`] operation must be called on the same [`DomainParticipant`] object used to create the [`Publisher`].
 If [`DomainParticipant::delete_publisher()`] is called on a different [`DomainParticipant`], the operation will have no effect and it will return
 a PreconditionNotMet error.
		"""
		...

	def create_subscriber(self, qos: SubscriberQos | None  = None, a_listener: Any | None  = None, mask: list[StatusKind] = []) -> Subscriber :
		r"""
 This operation creates a [`Subscriber`] with the desired QoS policies and attaches to it the specified [`SubscriberListener`].
 If the specified QoS policies are not consistent, the operation will fail and no [`Subscriber`] will be created.
 The value [`QosKind::Default`] can be used to indicate that the [`Subscriber`] should be created with the
 default Subscriber QoS set in the factory. The use of this value is equivalent to the application obtaining the default
 Subscriber QoS by means of the operation [`Self::get_default_subscriber_qos()`] and using the resulting QoS to create the
 [`Subscriber`].
 The created [`Subscriber`] belongs to the [`DomainParticipant`] that is its factory.
 In case of failure, the operation will return an error and no [`Subscriber`] will be created.
		"""
		...

	def delete_subscriber(self, a_subscriber: Subscriber) -> None :
		r"""
 This operation deletes an existing [`Subscriber`].
 A [`Subscriber`] cannot be deleted if it has any attached [`DataReader`](crate::subscription::data_reader::DataReader) objects. If the [`DomainParticipant::delete_subscriber()`] operation is called on a
 [`Subscriber`] with existing [`DataReader`](crate::subscription::data_reader::DataReader) objects, it will return [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
 The [`DomainParticipant::delete_subscriber()`] operation must be called on the same [`DomainParticipant`] object used to create the Subscriber. If
 it is called on a different [`DomainParticipant`], the operation will have no effect and it will return
 [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
		"""
		...

	def create_topic(self, topic_name: str, type_: Any, qos: TopicQos | None  = None, a_listener: Any | None  = None, mask: list[StatusKind] = []) -> TopicDescription :
		r"""
 This operation creates a [`Topic`] with the desired QoS policies and attaches to it the specified [`TopicListener`].
 If the specified QoS policies are not consistent, the operation will fail and no [`Topic`] will be created.
 The value [`QosKind::Default`] can be used to indicate that the [`Topic`] should be created with the default Topic QoS
 set in the factory. The use of this value is equivalent to the application obtaining the default Topic QoS by means of the
 operation [`DomainParticipant::get_default_topic_qos`] and using the resulting QoS to create the [`Topic`].
 The created [`Topic`] belongs to the [`DomainParticipant`] that is its factory.
 In case of failure, the operation will return an error and no [`Topic`] will be created.
		"""
		...

	def delete_topic(self, a_topic: TopicDescription) -> None :
		r"""
 This operation deletes a [`Topic`].
 The deletion of a [`Topic`] is not allowed if there are any existing [`DataReader`](crate::subscription::data_reader::DataReader) or [`DataWriter`](crate::publication::data_writer::DataWriter)
 objects that are using the [`Topic`]. If the [`DomainParticipant::delete_topic()`] operation is called on a [`Topic`] with any of these existing objects attached to
 it, it will return [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
 The [`DomainParticipant::delete_topic()`] operation must be called on the same [`DomainParticipant`] object used to create the [`Topic`]. If [`DomainParticipant::delete_topic()`] is
 called on a different [`DomainParticipant`], the operation will have no effect and it will return [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
		"""
		...

	def lookup_topicdescription(self, topic_name: str) -> TopicDescription | None  :
		r"""
 This operation gives access to an existing locally-created [`Topic`], based on its name and type. The
 operation takes as argument the name of the [`Topic`] and the type as a generic type argument `Foo`.
 If a [`Topic`] of the same name already exists, it gives access to it, otherwise it returns a [`None`] value. The operation
 never blocks.
 The operation [`DomainParticipant::lookup_topicdescription()`] may be used to locate any locally-created [`Topic`].
 Unlike [`DomainParticipant::find_topic()`], the operation [`DomainParticipant::lookup_topicdescription()`] searches only among the locally created topics. Therefore, it should
 never create a new [`Topic`]. The [`Topic`] returned by [`DomainParticipant::lookup_topicdescription()`] does not require any extra
 deletion. It is still possible to delete the [`Topic`] returned by [`DomainParticipant::lookup_topicdescription()`], provided it has no readers or
 writers, but then it is really deleted and subsequent lookups will fail.
 If the operation fails to locate a [`Topic`], the operation succeeds and a [`None`] value is returned.
		"""
		...

	def get_builtin_subscriber(self) -> Subscriber :
		r"""
 This operation allows access to the built-in [`Subscriber`]. Each [`DomainParticipant`] contains several built-in [`Topic`] objects as
 well as corresponding [`DataReader`](crate::subscription::data_reader::DataReader) objects to access them. All these [`DataReader`](crate::subscription::data_reader::DataReader) objects belong to a single built-in [`Subscriber`].
 The built-in topics are used to communicate information about other [`DomainParticipant`], [`Topic`], [`DataReader`](crate::subscription::data_reader::DataReader), and [`DataWriter`](crate::publication::data_writer::DataWriter)
 objects.
		"""
		...

	def ignore_participant(self, handle: InstanceHandle) -> None :
		r"""
 This operation allows an application to instruct the Service to locally ignore a remote domain participant. From that point
 onwards the Service will locally behave as if the remote participant did not exist. This means it will ignore any topic,
 publication, or subscription that originates on that domain participant.
 This operation can be used, in conjunction with the discovery of remote participants offered by means of the
 *DCPSParticipant* built-in [`Topic`], to provide, for example, access control.
 Application data can be associated with a [`DomainParticipant`] by means of the [`UserDataQosPolicy`](crate::infrastructure::qos_policy::UserDataQosPolicy).
 This application data is propagated as a field in the built-in topic and can be used by an application to implement its own access control policy.
 The domain participant to ignore is identified by the `handle` argument. This handle is the one that appears in the [`SampleInfo`](crate::subscription::sample_info::SampleInfo)
 retrieved when reading the data-samples available for the built-in DataReader to the *DCPSParticipant* topic. The built-in
 [`DataReader`](crate::subscription::data_reader::DataReader) is read with the same read/take operations used for any DataReader.
 The [`DomainParticipant::ignore_participant()`] operation is not reversible.
		"""
		...

	def ignore_topic(self, handle: InstanceHandle) -> None :
		r"""
 This operation allows an application to instruct the Service to locally ignore a remote topic. This means it will locally ignore any
 publication or subscription to the Topic.
 This operation can be used to save local resources when the application knows that it will never publish or subscribe to data
 under certain topics.
 The Topic to ignore is identified by the handle argument. This handle is the one that appears in the [`SampleInfo`](crate::subscription::sample_info::SampleInfo) retrieved when
 reading the data-samples from the built-in [`DataReader`](crate::subscription::data_reader::DataReader) to the *DCPSTopic* topic.
 The [`DomainParticipant::ignore_topic()`] operation is not reversible.
		"""
		...

	def ignore_publication(self, handle: InstanceHandle) -> None :
		r"""
 This operation allows an application to instruct the Service to locally ignore a remote publication; a publication is defined by
 the association of a topic name, and user data and partition set on the Publisher. After this call, any data written related to that publication will be ignored.
 The DataWriter to ignore is identified by the handle argument. This handle is the one that appears in the [`SampleInfo`](crate::subscription::sample_info::SampleInfo) retrieved
 when reading the data-samples from the built-in [`DataReader`](crate::subscription::data_reader::DataReader) to the *DCPSPublication* topic.
 The [`DomainParticipant::ignore_publication()`] operation is not reversible.
		"""
		...

	def ignore_subscription(self, handle: InstanceHandle) -> None :
		r"""
 This operation allows an application to instruct the Service to locally ignore a remote subscription; a subscription is defined by
 the association of a topic name, and user data and partition set on the Subscriber.
 After this call, any data received related to that subscription will be ignored.
 The DataReader to ignore is identified by the handle argument. This handle is the one that appears in the [`SampleInfo`](crate::subscription::sample_info::SampleInfo)
 retrieved when reading the data-samples from the built-in [`DataReader`](crate::subscription::data_reader::DataReader) to the *DCPSSubscription* topic.
 The [`DomainParticipant::ignore_subscription()`] operation is not reversible.
		"""
		...

	def get_domain_id(self) -> int :
		r"""
 This operation retrieves the [`DomainId`] used to create the DomainParticipant. The [`DomainId`] identifies the DDS domain to
 which the [`DomainParticipant`] belongs. Each DDS domain represents a separate data *communication plane* isolated from other domains.
		"""
		...

	def delete_contained_entities(self) -> None :
		r"""
 This operation deletes all the entities that were created by means of the *create* operations on the DomainParticipant. That is,
 it deletes all contained [`Publisher`], [`Subscriber`] and [`Topic`] entities.
 Prior to deleting each contained entity, this operation will recursively call the corresponding `delete_contained_entities()`
 operation on each contained entity (if applicable). This pattern is applied recursively. In this manner the operation
 [`DomainParticipant::delete_contained_entities()`] will end up deleting all the entities recursively contained in the
 [`DomainParticipant`], that is also the [`DataWriter`](crate::publication::data_writer::DataWriter), [`DataReader`](crate::subscription::data_reader::DataReader).
 The operation will return [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError) if the any of the contained entities is in a state where it cannot be
 deleted.
 Once this operation returns successfully, the application may delete the [`DomainParticipant`] knowing that it has no
 contained entities.
		"""
		...

	def assert_liveliness(self) -> None :
		r"""
 This operation manually asserts the liveliness of the [`DomainParticipant`]. This is used in combination
 with the [`LivelinessQosPolicy`](crate::infrastructure::qos_policy::LivelinessQosPolicy)
 to indicate to the Service that the entity remains active.
 This operation needs to only be used if the [`DomainParticipant`] contains  [`DataWriter`](crate::publication::data_writer::DataWriter) entities with the LIVELINESS set to
 MANUAL_BY_PARTICIPANT and it only affects the liveliness of those  [`DataWriter`](crate::publication::data_writer::DataWriter) entities. Otherwise, it has no effect.
 NOTE: Writing data via the write operation on a  [`DataWriter`](crate::publication::data_writer::DataWriter) asserts liveliness on the DataWriter itself and its
 [`DomainParticipant`]. Consequently the use of this operation is only needed if the application is not writing data regularly.
		"""
		...

	def set_default_publisher_qos(self, qos: PublisherQos | None ) -> None :
		r"""
 This operation sets a default value of the Publisher QoS policies which will be used for newly created [`Publisher`] entities in the
 case where the QoS policies are defaulted in the [`DomainParticipant::create_publisher()`] operation.
 This operation will check that the resulting policies are self consistent; if they are not, the operation will have no effect and
 return [`DdsError::InconsistenPolicy`](crate::infrastructure::error::DdsError).
 The special value [`QosKind::Default`] may be passed to this operation to indicate that the default QoS should be
 reset back to the initial values the factory would use, that is the values the default values of [`PublisherQos`].
		"""
		...

	def get_default_publisher_qos(self) -> PublisherQos :
		r"""
 This operation retrieves the default value of the Publisher QoS, that is, the QoS policies which will be used for newly created
 [`Publisher`] entities in the case where the QoS policies are defaulted in the [`DomainParticipant::create_publisher()`] operation.
 The values retrieved by this operation will match the set of values specified on the last successful call to
 [`DomainParticipant::set_default_publisher_qos()`], or else, if the call was never made, the default values of the [`PublisherQos`].
		"""
		...

	def set_default_subscriber_qos(self, qos: SubscriberQos | None ) -> None :
		r"""
 This operation sets a default value of the Subscriber QoS policies that will be used for newly created [`Subscriber`] entities in the
 case where the QoS policies are defaulted in the [`DomainParticipant::create_subscriber()`] operation.
 This operation will check that the resulting policies are self consistent; if they are not, the operation will have no effect and
 return [`DdsError::InconsistenPolicy`](crate::infrastructure::error::DdsError).
 The special value [`QosKind::Default`] may be passed to this operation to indicate that the default QoS should be
 reset back to the initial values the factory would use, that is the default values of [`SubscriberQos`].
		"""
		...

	def get_default_subscriber_qos(self) -> SubscriberQos :
		r"""
 This operation retrieves the default value of the Subscriber QoS, that is, the QoS policies which will be used for newly created
 [`Subscriber`] entities in the case where the QoS policies are defaulted in the [`DomainParticipant::create_subscriber()`] operation.
 The values retrieved by this operation will match the set of values specified on the last successful call to
 [`DomainParticipant::set_default_subscriber_qos()`], or else, if the call was never made, the default values of [`SubscriberQos`].
		"""
		...

	def set_default_topic_qos(self, qos: TopicQos | None ) -> None :
		r"""
 This operation sets a default value of the Topic QoS policies which will be used for newly created [`Topic`] entities in the case
 where the QoS policies are defaulted in the [`DomainParticipant::create_topic`] operation.
 This operation will check that the resulting policies are self consistent; if they are not, the operation will have no effect and
 return [`DdsError::InconsistenPolicy`](crate::infrastructure::error::DdsError).
 The special value [`QosKind::Default`] may be passed to this operation to indicate that the default QoS should be reset
 back to the initial values the factory would use, that is the default values of [`TopicQos`].
		"""
		...

	def get_default_topic_qos(self) -> TopicQos :
		r"""
 This operation retrieves the default value of the Topic QoS, that is, the QoS policies that will be used for newly created [`Topic`]
 entities in the case where the QoS policies are defaulted in the [`DomainParticipant::create_topic()`] operation.
 The values retrieved by this operation will match the set of values specified on the last successful call to
 [`DomainParticipant::set_default_topic_qos()`], or else, if the call was never made, the default values of [`TopicQos`]
		"""
		...

	def get_discovered_participants(self) -> list[InstanceHandle] :
		r"""
 This operation retrieves the list of DomainParticipants that have been discovered in the domain and that the application has not
 indicated should be *ignored* by means of the [`DomainParticipant::ignore_participant()`] operation.
		"""
		...

	def get_discovered_participant_data(self, participant_handle: InstanceHandle) -> ParticipantBuiltinTopicData :
		r"""
 This operation retrieves information on a [`DomainParticipant`] that has been discovered on the network. The participant must
 be in the same domain as the participant on which this operation is invoked and must not have been *ignored* by means of the
 [`DomainParticipant::ignore_participant()`] operation.
 The participant_handle must correspond to such a DomainParticipant. Otherwise, the operation will fail and return
 [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
 Use the operation [`DomainParticipant::get_discovered_participants()`] to find the DomainParticipants that are currently discovered.
		"""
		...

	def get_discovered_topics(self) -> list[InstanceHandle] :
		r"""
 This operation retrieves the list of Topics that have been discovered in the domain and that the application has not indicated
 should be *ignored* by means of the [`DomainParticipant::ignore_topic()`] operation.
		"""
		...

	def get_discovered_topic_data(self, topic_handle: InstanceHandle) -> TopicBuiltinTopicData :
		r"""
 This operation retrieves information on a Topic that has been discovered on the network. The topic must have been created by
 a participant in the same domain as the participant on which this operation is invoked and must not have been *ignored* by
 means of the [`DomainParticipant::ignore_topic()`] operation.
 The `topic_handle` must correspond to such a topic. Otherwise, the operation will fail and return
 [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
 Use the operation [`DomainParticipant::get_discovered_topics()`] to find the topics that are currently discovered.
		"""
		...

	def contains_entity(self, a_handle: InstanceHandle) -> bool :
		r"""
 This operation checks whether or not the given `a_handle` represents an Entity that was created from the [`DomainParticipant`].
 The containment applies recursively. That is, it applies both to entities ([`Topic`], [`Publisher`], or [`Subscriber`]) created
 directly using the [`DomainParticipant`] as well as entities created using a contained [`Publisher`], or [`Subscriber`] as the factory, and
 so forth.
 The instance handle for an Entity may be obtained from built-in topic data, from various statuses, or from the Entity operation
 `get_instance_handle`.
		"""
		...

	def get_current_time(self) -> Time :
		r"""
 This operation returns the current value of the time that the service uses to time-stamp data-writes and to set the reception timestamp
 for the data-updates it receives.
		"""
		...

	def set_qos(self, qos: DomainParticipantQos | None ) -> None :
		r"""
 This operation is used to set the QoS policies of the Entity and replacing the values of any policies previously set.
 Certain policies are *immutable;* they can only be set at Entity creation time, or before the entity is made enabled.
 If [`Self::set_qos()`] is invoked after the Entity is enabled and it attempts to change the value of an *immutable* policy, the operation will
 fail and returns [`DdsError::ImmutablePolicy`](crate::infrastructure::error::DdsError).
 Certain values of QoS policies can be incompatible with the settings of the other policies. This operation will also fail if it specifies
 a set of values that once combined with the existing values would result in an inconsistent set of policies. In this case,
 the return value is [`DdsError::InconsistentPolicy`](crate::infrastructure::error::DdsError).
 The existing set of policies are only changed if the [`Self::set_qos()`] operation succeeds. This is indicated by the [`Ok`] return value. In all
 other cases, none of the policies is modified.
 The parameter `qos` can be set to [`QosKind::Default`] to indicate that the QoS of the Entity should be changed to match the current default QoS set in the Entity's factory.
 The operation [`Self::set_qos()`] cannot modify the immutable QoS so a successful return of the operation indicates that the mutable QoS for the Entity has been
 modified to match the current default for the Entity's factory.
		"""
		...

	def get_qos(self) -> DomainParticipantQos :
		r"""
 This operation allows access to the existing set of [`DomainParticipantQos`] policies.
		"""
		...

	def set_listener(self, a_listener: Any | None  = None, mask: list[StatusKind] = []) -> None :
		r"""
 This operation installs a Listener on the Entity. The listener will only be invoked on the changes of communication status
 indicated by the specified mask. It is permitted to use [`None`] as the value of the listener. The [`None`] listener behaves
 as a Listener whose operations perform no action.
 Only one listener can be attached to each Entity. If a listener was already set, the operation [`Self::set_listener()`] will replace it with the
 new one. Consequently if the value [`None`] is passed for the listener parameter to the [`Self::set_listener()`] operation, any existing listener
 will be removed.
		"""
		...

	def get_status_changes(self) -> list[StatusKind] :
		r"""
 This operation retrieves the list of communication statuses in the Entity that are 'triggered.' That is, the list of statuses whose
 value has changed since the last time the application read the status.
 When the entity is first created or if the entity is not enabled, all communication statuses are in the *untriggered* state so the
 list returned by the [`Self::get_status_changes`] operation will be empty.
 The list of statuses returned by the [`Self::get_status_changes`] operation refers to the status that are triggered on the Entity itself
 and does not include statuses that apply to contained entities.
		"""
		...

	def enable(self) -> None :
		r"""
 This operation enables the Entity. Entity objects can be created either enabled or disabled. This is controlled by the value of
 the [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) on the corresponding factory for the Entity.
 The default setting of [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) is such that, by default, it is not necessary to explicitly call enable on newly
 created entities.
 The [`Self::enable()`] operation is idempotent. Calling [`Self::enable()`] on an already enabled Entity returns [`Ok`] and has no effect.
 If an Entity has not yet been enabled, the following kinds of operations may be invoked on it:
 - Operations to set or get an Entity's QoS policies (including default QoS policies) and listener
 - [`Self::get_statuscondition()`]
 - Factory and lookup operations
 - [`Self::get_status_changes()`] and other get status operations (although the status of a disabled entity never changes)
 Other operations may explicitly state that they may be called on disabled entities; those that do not will return the error
 NotEnabled.
 It is legal to delete an Entity that has not been enabled by calling the proper operation on its factory.
 Entities created from a factory that is disabled, are created disabled regardless of the setting of the
 [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy).
 Calling enable on an Entity whose factory is not enabled will fail and return [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
 If the `autoenable_created_entities` field of [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) is set to [`true`], the [`Self::enable()`] operation on the factory will
 automatically enable all entities created from the factory.
 The Listeners associated with an entity are not called until the entity is enabled. Conditions associated with an entity that is not
 enabled are *inactive*, that is, the operation [`StatusCondition::get_trigger_value()`] will always return `false`.
		"""
		...

	def get_instance_handle(self) -> InstanceHandle :
		r"""
 This operation returns the [`InstanceHandle`] that represents the Entity.
		"""
		...


class DomainParticipantFactory:
	r"""
 The sole purpose of this class is to allow the creation and destruction of [`DomainParticipant`] objects.
 [`DomainParticipantFactory`] itself has no factory. It is a pre-existing singleton object that can be accessed by means of the
 [`DomainParticipantFactory::get_instance`] operation.
	"""
	def get_instance() -> DomainParticipantFactory :
		r"""
 This operation returns the [`DomainParticipantFactory`] singleton. The operation is idempotent, that is, it can be called multiple
 times without side-effects and it will return the same [`DomainParticipantFactory`] instance.
		"""
		...

	def create_participant(self, domain_id: int, qos: DomainParticipantQos | None  = None, a_listener: Any | None  = None, mask: list[StatusKind] = []) -> DomainParticipant :
		r"""
 This operation creates a new [`DomainParticipant`] object. The [`DomainParticipant`] signifies that the calling application intends
 to join the Domain identified by the `domain_id` argument.
 If the specified QoS policies are not consistent, the operation will fail and no [`DomainParticipant`] will be created.
 The value [`QosKind::Default`] can be used to indicate that the [`DomainParticipant`] should be created
 with the default DomainParticipant QoS set in the factory. The use of this value is equivalent to the application obtaining the
 default DomainParticipant QoS by means of the operation [`DomainParticipantFactory::get_default_participant_qos`] and using the resulting
 QoS to create the [`DomainParticipant`].
		"""
		...

	def delete_participant(self, a_participant: DomainParticipant) -> None :
		r"""
 This operation deletes an existing [`DomainParticipant`]. This operation can only be invoked if all domain entities belonging to
 the participant have already been deleted otherwise the error [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError::PreconditionNotMet) is returned. If the
 participant has been previously deleted this operation returns the error [`DdsError::AlreadyDeleted`](crate::infrastructure::error::DdsError::AlreadyDeleted).
		"""
		...

	def lookup_participant(self, domain_id: int) -> DomainParticipant | None  :
		r"""
 This operation retrieves a previously created [`DomainParticipant`] belonging to the specified domain_id. If no such
 [`DomainParticipant`] exists, the operation will return a [`None`] value.
 If multiple [`DomainParticipant`] entities belonging to that domain_id exist, then the operation will return one of them. It is not
 specified which one.
		"""
		...

	def set_default_participant_qos(self, qos: DomainParticipantQos | None ) -> None :
		r"""
 This operation sets a default value of the [`DomainParticipantQos`] policies which will be used for newly created
 [`DomainParticipant`] entities in the case where the QoS policies are defaulted in the [`DomainParticipantFactory::create_participant`] operation.
 This operation will check that the resulting policies are self consistent; if they are not, the operation will have no effect and
 return a [`DdsError::InconsistentPolicy`](crate::infrastructure::error::DdsError::InconsistentPolicy).
		"""
		...

	def get_default_participant_qos(self) -> DomainParticipantQos :
		r"""
 This operation retrieves the default value of the [`DomainParticipantQos`], that is, the QoS policies which will be used for
 newly created [`DomainParticipant`] entities in the case where the QoS policies are defaulted in the [`DomainParticipantFactory::create_participant`]
 operation.
 The values retrieved by [`DomainParticipantFactory::get_default_participant_qos`] will match the set of values specified on the last successful call to
 [`DomainParticipantFactory::set_default_participant_qos`], or else, if the call was never made, the default value of [`DomainParticipantQos`].
		"""
		...

	def set_qos(self, qos: DomainParticipantFactoryQos | None ) -> None :
		r"""
 This operation sets the value of the [`DomainParticipantFactoryQos`] policies. These policies control the behavior of the object
 a factory for entities.
 Note that despite having QoS, the [`DomainParticipantFactory`] is not an Entity.
 This operation will check that the resulting policies are self consistent; if they are not, the operation will have no effect and
 return a [`DdsError::InconsistentPolicy`](crate::infrastructure::error::DdsError::InconsistentPolicy).
		"""
		...

	def get_qos(self) -> DomainParticipantFactoryQos :
		r"""
 This operation returns the value of the [`DomainParticipantFactoryQos`] policies.
		"""
		...


class BuiltInTopicKey:
	def get_value(self) -> list[int] :
		...


class ParticipantBuiltinTopicData:
	def get_key(self) -> BuiltInTopicKey :
		...

	def get_user_data(self) -> UserDataQosPolicy :
		...


class TopicBuiltinTopicData:
	def get_key(self) -> BuiltInTopicKey :
		...

	def get_name(self) -> str :
		...

	def get_type_name(self) -> str :
		...

	def get_durability(self) -> DurabilityQosPolicy :
		...

	def get_deadline(self) -> DeadlineQosPolicy :
		...

	def get_latency_budget(self) -> LatencyBudgetQosPolicy :
		...

	def get_liveliness(self) -> LivelinessQosPolicy :
		...

	def get_reliability(self) -> ReliabilityQosPolicy :
		...

	def get_transport_priority(self) -> TransportPriorityQosPolicy :
		...

	def get_lifespan(self) -> LifespanQosPolicy :
		...

	def get_destination_order(self) -> DestinationOrderQosPolicy :
		...

	def get_history(self) -> HistoryQosPolicy :
		...

	def get_resource_limits(self) -> ResourceLimitsQosPolicy :
		...

	def get_ownership(self) -> OwnershipQosPolicy :
		...

	def get_topic_data(self) -> TopicDataQosPolicy :
		...


class PublicationBuiltinTopicData:
	def get_key(self) -> BuiltInTopicKey :
		...

	def participant_key(self) -> BuiltInTopicKey :
		...

	def topic_name(self) -> str :
		...

	def get_type_name(self) -> str :
		...

	def get_durability(self) -> DurabilityQosPolicy :
		...

	def get_deadline(self) -> DeadlineQosPolicy :
		...

	def get_latency_budget(self) -> LatencyBudgetQosPolicy :
		...

	def get_liveliness(self) -> LivelinessQosPolicy :
		...

	def get_reliability(self) -> ReliabilityQosPolicy :
		...

	def get_lifespan(self) -> LifespanQosPolicy :
		...

	def get_user_data(self) -> UserDataQosPolicy :
		...

	def get_ownership(self) -> OwnershipQosPolicy :
		...

	def get_destination_order(self) -> DestinationOrderQosPolicy :
		...

	def get_presentation(self) -> PresentationQosPolicy :
		...

	def get_partition(self) -> PartitionQosPolicy :
		...

	def get_topic_data(self) -> TopicDataQosPolicy :
		...

	def get_group_data(self) -> GroupDataQosPolicy :
		...


class SubscriptionBuiltinTopicData:
	def get_key(self) -> BuiltInTopicKey :
		...

	def participant_key(self) -> BuiltInTopicKey :
		...

	def topic_name(self) -> str :
		...

	def get_type_name(self) -> str :
		...

	def get_durability(self) -> DurabilityQosPolicy :
		...

	def get_deadline(self) -> DeadlineQosPolicy :
		...

	def get_latency_budget(self) -> LatencyBudgetQosPolicy :
		...

	def get_liveliness(self) -> LivelinessQosPolicy :
		...

	def get_reliability(self) -> ReliabilityQosPolicy :
		...

	def get_ownership(self) -> OwnershipQosPolicy :
		...

	def get_destination_order(self) -> DestinationOrderQosPolicy :
		...

	def get_user_data(self) -> UserDataQosPolicy :
		...

	def get_time_based_filter(self) -> TimeBasedFilterQosPolicy :
		...

	def get_presentation(self) -> PresentationQosPolicy :
		...

	def get_partition(self) -> PartitionQosPolicy :
		...

	def get_topic_data(self) -> TopicDataQosPolicy :
		...

	def get_group_data(self) -> GroupDataQosPolicy :
		...


class Duration:
	def __init__(self, sec: int, nanosec: int) -> None :
		...

	def get_sec(self) -> int :
		...

	def get_nanosec(self) -> int :
		...


class DurationKind_Finite:
	def __init__(self, duration:Duration ) -> None: ...
class DurationKind_Infinite:
	def __init__(self ) -> None: ...
class DurationKind: 
	Finite = DurationKind_Finite
	Infinite = DurationKind_Infinite

class Time:
	def __init__(self, sec: int, nanosec: int) -> None :
		...

	def get_sec(self) -> int :
		...

	def get_nanosec(self) -> int :
		...


class Length_Unlimited:
	def __init__(self ) -> None: ...
class Length_Limited:
	def __init__(self, length:int ) -> None: ...
class Length: 
	Unlimited = Length_Unlimited
	Limited = Length_Limited

class UserDataQosPolicy:
	def __init__(self, value: list[int]) -> None :
		...

	def get_value(self) -> list[int] :
		...

	def set_value(self, value: list[int])  :
		...


class EntityFactoryQosPolicy:
	def __init__(self, autoenable_created_entities: bool) -> None :
		...

	def get_autoenable_created_entities(self) -> bool :
		...

	def set_autoenable_created_entities(self, value: bool)  :
		...


class TopicDataQosPolicy:
	def __init__(self, value: list[int]) -> None :
		...

	def get_value(self) -> list[int] :
		...

	def set_value(self, value: list[int])  :
		...


class DurabilityQosPolicyKind: 
	Volatile = 0
	TransientLocal = 1
	Transient = 2
	Persistent = 3

class DurabilityQosPolicy:
	def __init__(self, kind: DurabilityQosPolicyKind) -> None :
		...

	def get_kind(self) -> DurabilityQosPolicyKind :
		...

	def set_kind(self, value: DurabilityQosPolicyKind)  :
		...


class DeadlineQosPolicy:
	def __init__(self, period: DurationKind) -> None :
		...

	def get_period(self) -> DurationKind :
		...

	def set_period(self, value: DurationKind)  :
		...


class LatencyBudgetQosPolicy:
	def __init__(self, duration: DurationKind) -> None :
		...

	def get_duration(self) -> DurationKind :
		...

	def set_duration(self, value: DurationKind)  :
		...


class LivelinessQosPolicyKind: 
	Automatic = 0
	ManualByParticipant = 1
	ManualByTopic = 2

class LivelinessQosPolicy:
	def __init__(self, kind: LivelinessQosPolicyKind, lease_duration: DurationKind) -> None :
		...

	def get_kind(self) -> LivelinessQosPolicyKind :
		...

	def set_kind(self, value: LivelinessQosPolicyKind)  :
		...

	def get_lease_duration(self) -> DurationKind :
		...

	def set_lease_duration(self, value: DurationKind)  :
		...


class ReliabilityQosPolicyKind: 
	BestEffort = 0
	Reliable = 1

class ReliabilityQosPolicy:
	def __init__(self, kind: ReliabilityQosPolicyKind, max_blocking_time: DurationKind) -> None :
		...

	def get_kind(self) -> ReliabilityQosPolicyKind :
		...

	def set_kind(self, value: ReliabilityQosPolicyKind)  :
		...

	def get_max_blocking_time(self) -> DurationKind :
		...

	def set_max_blocking_time(self, value: DurationKind)  :
		...


class DestinationOrderQosPolicyKind: 
	ByReceptionTimestamp = 0
	BySourceTimestamp = 1

class DestinationOrderQosPolicy:
	def __init__(self, kind: DestinationOrderQosPolicyKind) -> None :
		...

	def get_kind(self) -> DestinationOrderQosPolicyKind :
		...

	def set_kind(self, value: DestinationOrderQosPolicyKind)  :
		...


class HistoryQosPolicyKind_KeepLast:
	def __init__(self, depth:int ) -> None: ...
class HistoryQosPolicyKind_KeepAll:
	def __init__(self ) -> None: ...
class HistoryQosPolicyKind: 
	KeepLast = HistoryQosPolicyKind_KeepLast
	KeepAll = HistoryQosPolicyKind_KeepAll

class HistoryQosPolicy:
	def __init__(self, kind: HistoryQosPolicyKind) -> None :
		...

	def get_kind(self) -> HistoryQosPolicyKind :
		...

	def set_kind(self, value: HistoryQosPolicyKind)  :
		...


class ResourceLimitsQosPolicy:
	def __init__(self, max_samples: Length, max_instances: Length, max_samples_per_instance: Length) -> None :
		...

	def get_max_samples(self) -> Length :
		...

	def set_max_samples(self, value: Length)  :
		...

	def get_max_instances(self) -> Length :
		...

	def set_max_instances(self, value: Length)  :
		...

	def get_max_samples_per_instance(self) -> Length :
		...

	def set_max_samples_per_instance(self, value: Length)  :
		...


class TransportPriorityQosPolicy:
	def __init__(self, value: int) -> None :
		...

	def get_value(self) -> int :
		...

	def set_value(self, value: int)  :
		...


class LifespanQosPolicy:
	def __init__(self, duration: DurationKind) -> None :
		...

	def get_duration(self) -> DurationKind :
		...

	def set_duration(self, value: DurationKind)  :
		...


class OwnershipQosPolicyKind: 
	Shared = 0
	Exclusive = 1

class OwnershipQosPolicy:
	def __init__(self, kind: OwnershipQosPolicyKind) -> None :
		...

	def get_kind(self) -> OwnershipQosPolicyKind :
		...

	def set_kind(self, value: OwnershipQosPolicyKind)  :
		...


class OwnershipStrengthQosPolicy:
	pass


class GroupDataQosPolicy:
	def __init__(self, value: list[int]) -> None :
		...

	def get_value(self) -> list[int] :
		...

	def set_value(self, value: list[int])  :
		...


class PartitionQosPolicy:
	def __init__(self, name: list[str]) -> None :
		...

	def get_name(self) -> list[str] :
		...

	def set_name(self, value: list[str])  :
		...


class PresentationQosPolicyAccessScopeKind: 
	Instance = 0
	Topic = 1

class PresentationQosPolicy:
	def __init__(self, access_scope: PresentationQosPolicyAccessScopeKind, coherent_access: bool, ordered_access: bool) -> None :
		...

	def get_access_scope(self) -> PresentationQosPolicyAccessScopeKind :
		...

	def set_access_scope(self, value: PresentationQosPolicyAccessScopeKind)  :
		...

	def get_coherent_access(self) -> bool :
		...

	def set_coherent_access(self, value: bool)  :
		...

	def get_ordered_access(self) -> bool :
		...

	def set_ordered_access(self, value: bool)  :
		...


class WriterDataLifecycleQosPolicy:
	def __init__(self, autodispose_unregistered_instances: bool) -> None :
		...

	def get_autodispose_unregistered_instances(self) -> bool :
		...

	def set_autodispose_unregistered_instances(self, value: bool)  :
		...


class TimeBasedFilterQosPolicy:
	def __init__(self, minimum_separation: DurationKind) -> None :
		...

	def get_minimum_separation(self) -> DurationKind :
		...

	def set_minimum_separation(self, value: DurationKind)  :
		...


class ReaderDataLifecycleQosPolicy:
	def __init__(self, autopurge_nowriter_samples_delay: DurationKind, autopurge_disposed_samples_delay: DurationKind) -> None :
		...

	def get_autopurge_nowriter_samples_delay(self) -> DurationKind :
		...

	def set_autopurge_nowriter_samples_delay(self, value: DurationKind)  :
		...

	def get_autopurge_disposed_samples_delay(self) -> DurationKind :
		...

	def set_autopurge_disposed_samples_delay(self, value: DurationKind)  :
		...


class DataRepresentationQosPolicy:
	pass


class StatusKind: 
	InconsistentTopic = 0
	OfferedDeadlineMissed = 1
	RequestedDeadlineMissed = 2
	OfferedIncompatibleQos = 3
	RequestedIncompatibleQos = 4
	SampleLost = 5
	SampleRejected = 6
	DataOnReaders = 7
	DataAvailable = 8
	LivelinessLost = 9
	LivelinessChanged = 10
	PublicationMatched = 11
	SubscriptionMatched = 12

class InconsistentTopicStatus:
	def get_total_count(self) -> int :
		...

	def get_total_count_change(self) -> int :
		...


class SampleLostStatus:
	def get_total_count(self) -> int :
		...

	def get_total_count_change(self) -> int :
		...


class SampleRejectedStatusKind: 
	NotRejected = 0
	RejectedByInstancesLimit = 1
	RejectedBySamplesLimit = 2
	RejectedBySamplesPerInstanceLimit = 3

class SampleRejectedStatus:
	def get_total_count(self) -> int :
		...

	def get_total_count_change(self) -> int :
		...

	def get_last_reason(self) -> SampleRejectedStatusKind :
		...

	def get_last_instance_handle(self) -> InstanceHandle :
		...


class LivelinessLostStatus:
	def get_total_count(self) -> int :
		...

	def get_total_count_change(self) -> int :
		...


class LivelinessChangedStatus:
	def get_alive_count(self) -> int :
		...

	def get_not_alive_count(self) -> int :
		...

	def get_alive_count_change(self) -> int :
		...

	def get_not_alive_count_change(self) -> int :
		...

	def get_last_publication_handle(self) -> InstanceHandle :
		...


class OfferedDeadlineMissedStatus:
	def get_total_count(self) -> int :
		...

	def get_total_count_change(self) -> int :
		...

	def get_last_instance_handle(self) -> InstanceHandle :
		...


class RequestedDeadlineMissedStatus:
	def get_total_count(self) -> int :
		...

	def get_total_count_change(self) -> int :
		...

	def get_last_instance_handle(self) -> InstanceHandle :
		...


class QosPolicyCount:
	def get_policy_id(self) -> int :
		...

	def get_count(self) -> int :
		...


class OfferedIncompatibleQosStatus:
	def get_total_count(self) -> int :
		...

	def get_total_count_change(self) -> int :
		...

	def get_last_policy_id(self) -> int :
		...

	def get_policies(self) -> list[QosPolicyCount] :
		...


class RequestedIncompatibleQosStatus:
	def get_total_count(self) -> int :
		...

	def get_total_count_change(self) -> int :
		...

	def get_last_policy_id(self) -> int :
		...

	def get_policies(self) -> list[QosPolicyCount] :
		...


class PublicationMatchedStatus:
	def get_total_count(self) -> int :
		...

	def get_total_count_change(self) -> int :
		...

	def get_last_subscription_handle(self) -> InstanceHandle :
		...

	def get_current_count(self) -> int :
		...

	def get_current_count_change(self) -> int :
		...


class SubscriptionMatchedStatus:
	def get_total_count(self) -> int :
		...

	def get_total_count_change(self) -> int :
		...

	def get_last_publication_handle(self) -> InstanceHandle :
		...

	def get_current_count(self) -> int :
		...

	def get_current_count_change(self) -> int :
		...


class StatusCondition:
	def get_enabled_statuses(self) -> list[StatusKind] :
		...

	def set_enabled_statuses(self, mask: list[StatusKind]) -> None :
		...

	def get_trigger_value(self) -> bool :
		...


class InstanceHandle:
	pass


class Condition_StatusCondition:
	def __init__(self, condition:StatusCondition ) -> None: ...
class Condition: 
	StatusCondition = Condition_StatusCondition

class WaitSet:
	def __init__(self, ) -> None :
		...

	def wait(self, timeout: Duration) -> list[Condition] :
		...

	def attach_condition(self, cond: Condition) -> None :
		...

	def detach_condition(self, cond: Condition) -> None :
		...

	def get_conditions(self) -> list[Condition] :
		...


class DomainParticipantFactoryQos:
	def __init__(self, entity_factory: EntityFactoryQosPolicy = ...) -> None :
		...


class DomainParticipantQos:
	def __init__(self, user_data: UserDataQosPolicy = ..., entity_factory: EntityFactoryQosPolicy = ...) -> None :
		...


class PublisherQos:
	def __init__(self, presentation: PresentationQosPolicy = ..., partition: PartitionQosPolicy = ..., group_data: GroupDataQosPolicy = ..., entity_factory: EntityFactoryQosPolicy = ...) -> None :
		...

	def get_presentation(self) -> PresentationQosPolicy :
		...

	def set_presentation(self, value: PresentationQosPolicy)  :
		...

	def get_partition(self) -> PartitionQosPolicy :
		...

	def set_partition(self, value: PartitionQosPolicy)  :
		...

	def get_group_data(self) -> GroupDataQosPolicy :
		...

	def set_group_data(self, value: GroupDataQosPolicy)  :
		...

	def get_entity_factory(self) -> EntityFactoryQosPolicy :
		...

	def set_entity_factory(self, value: EntityFactoryQosPolicy)  :
		...


class SubscriberQos:
	def __init__(self, presentation: PresentationQosPolicy = ..., partition: PartitionQosPolicy = ..., group_data: GroupDataQosPolicy = ..., entity_factory: EntityFactoryQosPolicy = ...) -> None :
		...


class TopicQos:
	def __init__(self, topic_data: TopicDataQosPolicy = ..., durability: DurabilityQosPolicy = ..., deadline: DeadlineQosPolicy = ..., latency_budget: LatencyBudgetQosPolicy = ..., liveliness: LivelinessQosPolicy = ..., reliability: ReliabilityQosPolicy = DEFAULT_RELIABILITY_QOS_POLICY_DATA_READER_AND_TOPICS, destination_order: DestinationOrderQosPolicy = ..., history: HistoryQosPolicy = ..., resource_limits: ResourceLimitsQosPolicy = ..., transport_priority: TransportPriorityQosPolicy = ..., lifespan: LifespanQosPolicy = ..., ownership: OwnershipQosPolicy = ..., representation: DataRepresentationQosPolicy = ...) -> None :
		...


class DataWriterQos:
	def __init__(self, durability: DurabilityQosPolicy = ..., deadline: DeadlineQosPolicy = ..., latency_budget: LatencyBudgetQosPolicy = ..., liveliness: LivelinessQosPolicy = ..., reliability: ReliabilityQosPolicy = DEFAULT_RELIABILITY_QOS_POLICY_DATA_WRITER, destination_order: DestinationOrderQosPolicy = ..., history: HistoryQosPolicy = ..., resource_limits: ResourceLimitsQosPolicy = ..., transport_priority: TransportPriorityQosPolicy = ..., lifespan: LifespanQosPolicy = ..., user_data: UserDataQosPolicy = ..., ownership: OwnershipQosPolicy = ..., ownership_strength: OwnershipStrengthQosPolicy = ..., writer_data_lifecycle: WriterDataLifecycleQosPolicy = ..., representation: DataRepresentationQosPolicy = ...) -> None :
		...


class DataReaderQos:
	def __init__(self, durability: DurabilityQosPolicy = ..., deadline: DeadlineQosPolicy = ..., latency_budget: LatencyBudgetQosPolicy = ..., liveliness: LivelinessQosPolicy = ..., reliability: ReliabilityQosPolicy = DEFAULT_RELIABILITY_QOS_POLICY_DATA_READER_AND_TOPICS, destination_order: DestinationOrderQosPolicy = ..., history: HistoryQosPolicy = ..., resource_limits: ResourceLimitsQosPolicy = ..., user_data: UserDataQosPolicy = ..., ownership: OwnershipQosPolicy = ..., time_based_filter: TimeBasedFilterQosPolicy = ..., reader_data_lifecycle: ReaderDataLifecycleQosPolicy = ..., representation: DataRepresentationQosPolicy = ...) -> None :
		...


class Subscriber:
	r"""
 A [`Subscriber`] is the object responsible for the actual reception of the data resulting from its subscriptions.

 A [`Subscriber`] acts on the behalf of one or several [`DataReader`] objects that are related to it. When it receives data (from the
 other parts of the system), it builds the list of concerned [`DataReader`] objects, and then indicates to the application that data is
 available, through its listener or by enabling related conditions.
	"""
	def create_datareader(self, a_topic: TopicDescription, qos: DataReaderQos | None  = None, a_listener: Any | None  = None, mask: list[StatusKind] = []) -> DataReader :
		r"""
 This operation creates a [`DataReader`]. The returned [`DataReader`] will be attached and belong to the [`Subscriber`].
 The [`DataReader`] returned by this operation has an associated [`Topic`] and a type `Foo`.
 The [`Topic`] passed to this operation must have been created from the same [`DomainParticipant`] that was used to create this
 [`Subscriber`]. If the [`Topic`] was created from a different [`DomainParticipant`], the operation will fail and
 return a [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError). In case of failure, the operation
 will return an error and no writer will be created.

 The special value [`QosKind::Default`] can be used to indicate that the [`DataReader`] should be created with the
 default qos set in the factory. The use of this value is equivalent to the application obtaining the default
 [`DataReaderQos`] by means of the operation [`Subscriber::get_default_datareader_qos`] and using the resulting qos
 to create the [`DataReader`]. A common application pattern to construct the [`DataReaderQos`] to ensure consistency with the
 associated [`TopicQos`] is to:
 1. Retrieve the QoS policies on the associated [`Topic`] by means of the [`Topic::get_qos`] operation.
 2. Retrieve the default [`DataReaderQos`] qos by means of the [`Subscriber::get_default_datareader_qos`] operation.
 3. Combine those two qos policies using the [`Subscriber::copy_from_topic_qos`] and selectively modify policies as desired and
 use the resulting [`DataReaderQos`] to construct the [`DataReader`].
		"""
		...

	def delete_datareader(self, a_datareader: DataReader) -> None :
		r"""
 This operation deletes a [`DataReader`] that belongs to the [`Subscriber`]. This operation must be called on the
 same [`Subscriber`] object used to create the [`DataReader`]. If [`Subscriber::delete_datareader`] is called on a
 different [`Subscriber`], the operation will have no effect and it will return [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
		"""
		...

	def lookup_datareader(self, topic_name: str) -> DataReader | None  :
		r"""
 This operation retrieves a previously created [`DataReader`] belonging to the [`Subscriber`] that is attached to a [`Topic`].
 If no such [`DataReader`] exists, the operation will succeed but return [`None`].
 If multiple [`DataReader`] attached to the [`Subscriber`] satisfy this condition, then the operation will return one of them. It is not
 specified which one.
 The use of this operation on the built-in [`Subscriber`] allows access to the built-in [`DataReader`] entities for the built-in topics.
		"""
		...

	def notify_datareaders(self) -> None :
		r"""
 This operation invokes the operation [`DataReaderListener::on_data_available`] on the listener objects attached to contained [`DataReader`]
 entities with a [`StatusKind::DataAvailable`] that is considered changed.
 This operation is typically invoked from the [`SubscriberListener::on_data_on_readers`] operation. That way the
 [`SubscriberListener`] can delegate to the [`DataReaderListener`] objects the handling of the data.
		"""
		...

	def get_participant(self) -> DomainParticipant :
		r"""
 This operation returns the [`DomainParticipant`] to which the [`Subscriber`] belongs.
		"""
		...

	def get_sample_lost_status(self) -> SampleLostStatus :
		r"""
 This operation allows access to the [`SampleLostStatus`].
		"""
		...

	def delete_contained_entities(self) -> None :
		r"""
 This operation deletes all the entities that were created by means of the [`Subscriber::create_datareader`] operations.
 That is, it deletes all contained [`DataReader`] objects.
 he operation will return [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError) if the any of the
 contained entities is in a state where it cannot be deleted.
 Once this operation returns successfully, the application may delete the [`Subscriber`] knowing that it has no
 contained [`DataReader`] objects.
		"""
		...

	def set_default_datareader_qos(self, qos: DataReaderQos | None ) -> None :
		r"""
 This operation sets a default value of the [`DataReaderQos`] which will be used for newly created [`DataReader`] entities in
 the case where the qos policies are defaulted in the [`Subscriber::create_datareader`] operation.
 This operation will check that the resulting policies are self consistent; if they are not, the operation will have no effect and
 return [`DdsError::InconsistentPolicy`](crate::infrastructure::error::DdsError).
 The special value [`QosKind::Default`] may be passed to this operation to indicate that the default qos should be
 reset back to the initial values the factory would use, that is the default value of [`DataReaderQos`].
		"""
		...

	def get_default_datareader_qos(self) -> DataReaderQos :
		r"""
 This operation retrieves the default value of the [`DataReaderQos`], that is, the qos policies which will be used for newly
 created [`DataReader`] entities in the case where the qos policies are defaulted in the [`Subscriber::create_datareader`] operation.
 The values retrieved by this operation will match the set of values specified on the last successful call to
 [`Subscriber::get_default_datareader_qos`], or else, if the call was never made, the default values of [`DataReaderQos`].
		"""
		...

	def set_qos(self, qos: SubscriberQos | None ) -> None :
		r"""
 This operation is used to set the QoS policies of the Entity and replacing the values of any policies previously set.
 Certain policies are *immutable;* they can only be set at Entity creation time, or before the entity is made enabled.
 If [`Self::set_qos()`] is invoked after the Entity is enabled and it attempts to change the value of an *immutable* policy, the operation will
 fail and returns [`DdsError::ImmutablePolicy`](crate::infrastructure::error::DdsError).
 Certain values of QoS policies can be incompatible with the settings of the other policies. This operation will also fail if it specifies
 a set of values that once combined with the existing values would result in an inconsistent set of policies. In this case,
 the return value is [`DdsError::InconsistentPolicy`](crate::infrastructure::error::DdsError).
 The existing set of policies are only changed if the [`Self::set_qos()`] operation succeeds. This is indicated by the [`Ok`] return value. In all
 other cases, none of the policies is modified.
 The parameter `qos` can be set to [`QosKind::Default`] to indicate that the QoS of the Entity should be changed to match the current default QoS set in the Entity's factory.
 The operation [`Self::set_qos()`] cannot modify the immutable QoS so a successful return of the operation indicates that the mutable QoS for the Entity has been
 modified to match the current default for the Entity's factory.
		"""
		...

	def get_qos(self) -> SubscriberQos :
		r"""
 This operation allows access to the existing set of [`SubscriberQos`] policies.
		"""
		...

	def set_listener(self, a_listener: Any | None  = None, mask: list[StatusKind] = []) -> None :
		r"""
 This operation installs a Listener on the Entity. The listener will only be invoked on the changes of communication status
 indicated by the specified mask. It is permitted to use [`None`] as the value of the listener. The [`None`] listener behaves
 as a Listener whose operations perform no action.
 Only one listener can be attached to each Entity. If a listener was already set, the operation [`Self::set_listener()`] will replace it with the
 new one. Consequently if the value [`None`] is passed for the listener parameter to the [`Self::set_listener()`] operation, any existing listener
 will be removed.
		"""
		...

	def get_statuscondition(self) -> StatusCondition :
		r"""
 This operation allows access to the [`StatusCondition`] associated with the Entity. The returned
 condition can then be added to a [`WaitSet`](crate::infrastructure::wait_set::WaitSet) so that the application can wait for specific status changes
 that affect the Entity.
		"""
		...

	def get_status_changes(self) -> list[StatusKind] :
		r"""
 This operation retrieves the list of communication statuses in the Entity that are 'triggered.' That is, the list of statuses whose
 value has changed since the last time the application read the status.
 When the entity is first created or if the entity is not enabled, all communication statuses are in the *untriggered* state so the
 list returned by the [`Self::get_status_changes`] operation will be empty.
 The list of statuses returned by the [`Self::get_status_changes`] operation refers to the status that are triggered on the Entity itself
 and does not include statuses that apply to contained entities.
		"""
		...

	def enable(self) -> None :
		r"""
 This operation enables the Entity. Entity objects can be created either enabled or disabled. This is controlled by the value of
 the [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) on the corresponding factory for the Entity.
 The default setting of [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) is such that, by default, it is not necessary to explicitly call enable on newly
 created entities.
 The [`Self::enable()`] operation is idempotent. Calling [`Self::enable()`] on an already enabled Entity returns [`Ok`] and has no effect.
 If an Entity has not yet been enabled, the following kinds of operations may be invoked on it:
 - Operations to set or get an Entity's QoS policies (including default QoS policies) and listener
 - [`Self::get_statuscondition()`]
 - Factory and lookup operations
 - [`Self::get_status_changes()`] and other get status operations (although the status of a disabled entity never changes)
 Other operations may explicitly state that they may be called on disabled entities; those that do not will return the error
 NotEnabled.
 It is legal to delete an Entity that has not been enabled by calling the proper operation on its factory.
 Entities created from a factory that is disabled, are created disabled regardless of the setting of the
 [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy).
 Calling enable on an Entity whose factory is not enabled will fail and return [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
 If the `autoenable_created_entities` field of [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) is set to [`true`], the [`Self::enable()`] operation on the factory will
 automatically enable all entities created from the factory.
 The Listeners associated with an entity are not called until the entity is enabled. Conditions associated with an entity that is not
 enabled are *inactive*, that is, the operation [`StatusCondition::get_trigger_value()`] will always return `false`.
		"""
		...

	def get_instance_handle(self) -> InstanceHandle :
		r"""
 This operation returns the [`InstanceHandle`] that represents the Entity.
		"""
		...


class SampleStateKind: 
	Read = 0
	NotRead = 1

class ViewStateKind: 
	New = 0
	NotNew = 1

class InstanceStateKind: 
	Alive = 0
	NotAliveDisposed = 1
	NotAliveNoWriters = 2

class SampleInfo:
	pass


class DataReader:
	r"""
 A [`DataReader`] allows the application (1) to declare the data it wishes to receive (i.e., make a subscription) and (2) to access the
 data received by the attached [`Subscriber`].

 A DataReader refers to exactly one [`Topic`] that identifies the data to be read. The subscription has a unique resulting type.
 The data-reader may give access to several instances of the resulting type, which can be distinguished from each other by their key.
	"""
	def read(self, max_samples: int, sample_states: list[SampleStateKind] = ANY_SAMPLE_STATE, view_states: list[ViewStateKind] = ANY_VIEW_STATE, instance_states: list[InstanceStateKind] = ANY_INSTANCE_STATE) -> list[Sample] :
		r"""
 This operation accesses a collection of [`Sample`] from the [`DataReader`]. The size of the returned collection will
 be limited to the specified `max_samples`. The properties of the data values collection and the setting of the
 [`PresentationQosPolicy`](crate::infrastructure::qos_policy::PresentationQosPolicy) may impose further limits
 on the size of the returned list:
 1. If [`PresentationQosPolicy::access_scope`](crate::infrastructure::qos_policy::PresentationQosPolicy) is
 [`PresentationQosPolicyAccessScopeKind::Instance`](crate::infrastructure::qos_policy::PresentationQosPolicyAccessScopeKind),
 then the returned collection is a list where samples belonging to the same data-instance are consecutive.
 2. If [`PresentationQosPolicy::access_scope`](crate::infrastructure::qos_policy::PresentationQosPolicy) is
 [`PresentationQosPolicyAccessScopeKind::Topic`](crate::infrastructure::qos_policy::PresentationQosPolicyAccessScopeKind) and
 [`PresentationQosPolicy::ordered_access`](crate::infrastructure::qos_policy::PresentationQosPolicy) is set to [`false`],
 then the returned collection is a list where samples belonging to the same data-instance are consecutive.
 3. If [`PresentationQosPolicy::access_scope`](crate::infrastructure::qos_policy::PresentationQosPolicy) is
 [`PresentationQosPolicyAccessScopeKind::Topic`](crate::infrastructure::qos_policy::PresentationQosPolicyAccessScopeKind) and
 [`PresentationQosPolicy::ordered_access`](crate::infrastructure::qos_policy::PresentationQosPolicy) is set to [`true`],
 then the returned collection is a list where samples belonging to the same instance may or may not be consecutive.
 This is because to preserve order it may be necessary to mix samples from different instances.

 In any case, the relative order between the samples of one instance is consistent with the
 [`DestinationOrderQosPolicy`](crate::infrastructure::qos_policy::DestinationOrderQosPolicy):
 - If [`DestinationOrderQosPolicyKind::ByReceptionTimestamp`](crate::infrastructure::qos_policy::DestinationOrderQosPolicyKind),
 samples belonging to the same instances will appear in the relative order in which there were received
 (FIFO, earlier samples ahead of the later samples).
 - If  [`DestinationOrderQosPolicyKind::BySourceTimestamp`](crate::infrastructure::qos_policy::DestinationOrderQosPolicyKind),
 samples belonging to the same instances will appear in the relative order implied by the `source_timestamp`
 (FIFO, smaller values of `source_timestamp` ahead of the larger values).

 Each [`Sample`] contains the data and a [`SampleInfo`] which provides information, such as the
 [`SampleInfo::source_timestamp`], the [`SampleInfo::sample_state`], [`SampleInfo::view_state`], and
 [`SampleInfo::instance_state`], etc., about the corresponding sample.
 Some elements in the returned collection may not have valid data. If the [`SampleInfo::instance_state`] is
 [`InstanceStateKind::NotAliveDisposed`] or [`InstanceStateKind::NotAliveNoWriters`], then the last sample
 for that instance in the collection, that is, the one whose `[`SampleInfo::sample_rank`]==0` does not contain
 valid data. Samples that contain no data do not count towards the limits imposed by the
 [`ResourceLimitsQosPolicy`](crate::infrastructure::qos_policy::ResourceLimitsQosPolicy).
 The act of reading a sample sets its [`SampleInfo::sample_state`] to [`SampleStateKind::Read`]. If the sample
 belongs to the most recent generation of the instance, it will also set the [`SampleInfo::view_state`]
 of the instance to [`ViewStateKind::NotNew`]. It will not affect the  [`SampleInfo::instance_state`] of the instance.

 If the DataReader has no samples that meet the constraints, the return value will be
 [`DdsError::NoData`](crate::infrastructure::error::DdsError).
		"""
		...

	def take(self, max_samples: int, sample_states: list[SampleStateKind] = ANY_SAMPLE_STATE, view_states: list[ViewStateKind] = ANY_VIEW_STATE, instance_states: list[InstanceStateKind] = ANY_INSTANCE_STATE) -> list[Sample] :
		r"""
 This operation accesses a collection of [`Sample`] from the [`DataReader`]. This operation uses the same
 logic as the [`DataReader::read`]. The only difference with read is that the
 sampled returned by [`DataReader::take`] will no longer be accessible to successive calls to read or take.
		"""
		...

	def read_next_sample(self) -> Sample :
		r"""
 This operation reads the next, non-previously accessed [`Sample`] value from the [`DataReader`].
 The implied order among the samples stored in the [`DataReader`] is the same as for the [`DataReader::read`]
 operation. This operation is semantically equivalent to the read operation where the input Data sequence has
 `max_samples=1`, the `sample_states = &[SampleStateKind::NotRead]`, `view_states=ANY_VIEW_STATE`, and
 `instance_states=ANY_INSTANCE_STATE`.
 This operation provides a simplified API to 'read' samples avoiding the need for the application to manage
 sequences and specify states.
		"""
		...

	def take_next_sample(self) -> Sample :
		r"""
 This operation takes the next, non-previously accessed [`Sample`] value from the [`DataReader`].
 The implied order among the samples stored in the [`DataReader`] is the same as for the [`DataReader::read`]
 operation. This operation is semantically equivalent to the read operation where the input Data sequence has
 `max_samples=1`, the `sample_states = &[SampleStateKind::NotRead]`, `view_states=ANY_VIEW_STATE`, and
 `instance_states=ANY_INSTANCE_STATE`.
 This operation provides a simplified API to 'take' samples avoiding the need for the application to manage
 sequences and specify states.
		"""
		...

	def read_instance(self, max_samples: int, a_handle: InstanceHandle, sample_states: list[SampleStateKind] = ANY_SAMPLE_STATE, view_states: list[ViewStateKind] = ANY_VIEW_STATE, instance_states: list[InstanceStateKind] = ANY_INSTANCE_STATE) -> list[Sample] :
		r"""
 This operation accesses a collection of [`Sample`] from the [`DataReader`]. The
 behavior is identical to [`DataReader::read`] except that all samples returned
 belong to the single specified instance whose handle is `a_handle`.
 Upon successful return, the collection will contain samples all belonging to the
 same instance. The corresponding [`SampleInfo`] verifies [`SampleInfo::instance_handle`] == a_handle.
 This operation return [`DdsError::BadParameter`](crate::infrastructure::error::DdsError)
 if the [`InstanceHandle`] `a_handle` does not correspond to an existing
 data object known to the [`DataReader`].
		"""
		...

	def take_instance(self, max_samples: int, a_handle: InstanceHandle, sample_states: list[SampleStateKind] = ANY_SAMPLE_STATE, view_states: list[ViewStateKind] = ANY_VIEW_STATE, instance_states: list[InstanceStateKind] = ANY_INSTANCE_STATE) -> list[Sample] :
		r"""
 This operation accesses a collection of [`Sample`] from the [`DataReader`]. The
 behavior is identical to [`DataReader::take`] except that all samples returned
 belong to the single specified instance whose handle is `a_handle`.
 Upon successful return, the collection will contain samples all belonging to the
 same instance. The corresponding [`SampleInfo`] verifies [`SampleInfo::instance_handle`] == a_handle.
 This operation return [`DdsError::BadParameter`](crate::infrastructure::error::DdsError)
 if the [`InstanceHandle`] `a_handle` does not correspond to an existing
 data object known to the [`DataReader`].
		"""
		...

	def read_next_instance(self, max_samples: int, previous_handle: InstanceHandle | None , sample_states: list[SampleStateKind] = ANY_SAMPLE_STATE, view_states: list[ViewStateKind] = ANY_VIEW_STATE, instance_states: list[InstanceStateKind] = ANY_INSTANCE_STATE) -> list[Sample] :
		r"""
 This operation accesses a collection of [`Sample`] from the [`DataReader`] where all the samples belong to a single instance.
 The behavior is similar to [`DataReader::read_instance`] except that the actual instance is not directly specified.
 Rather the samples will all belong to the 'next' instance with instance_handle 'greater' than the specified
 `previous_handle` that has available samples.
 This operation implies the existence of a total order *greater-than* relationship between the instance handles.
 The specifics of this relationship are not all important and are implementation specific. The important thing is that,
 according to the middleware, all instances are ordered relative to each other. This ordering is between the instance handles
 and it does not depend on the state of the instance (e.g., whether it has data or not) and must be defined even for
 instance handles that do not correspond to instances currently managed by the [`DataReader`].
 The behavior of this operation is as if [`DataReader::read_instance`] was invoked passing the smallest `instance_handle`
 among all the ones that (a) are greater than `previous_handle` and (b) have available samples (i.e., samples that meet the
 constraints imposed by the specified states). If [`None`] is used as the `previous_handle` argument the operation will
 return the samples for the instance which has the smallest instance_handle among allthe instances that contain available samples.
 The operation [`DataReader::read_next_instance`] is intended to be used in an application-driven iteration where the application starts by
 passing `previous_handle==None`, examines the samples returned, and then uses the [`SampleInfo::instance_handle`] returned in
 as the value of the `previous_handle` argument to the next call to [`DataReader::read_next_instance`]. The iteration continues
 until the operation returns the value [`DdsError::NoData`](crate::infrastructure::error::DdsError).
 Note that it is possible to call this operation with a `previous_handle` that does not correspond to an
 instance currently managed by the [`DataReader`]. One practical situation where this may occur is when an application is iterating
 though all the instances, takes all the samples of a [`InstanceStateKind::NotAliveNoWriters`] instance (at which point the
 instance information may be removed, and thus the handle becomes invalid) and tries to read the next instance.
 The behavior of this operation generally follows the same rules as the [`DataReader::read`] operation regarding the pre-conditions
 and post-conditions and returned values.
		"""
		...

	def take_next_instance(self, max_samples: int, previous_handle: InstanceHandle | None , sample_states: list[SampleStateKind] = ANY_SAMPLE_STATE, view_states: list[ViewStateKind] = ANY_VIEW_STATE, instance_states: list[InstanceStateKind] = ANY_INSTANCE_STATE) -> list[Sample] :
		r"""
 This operation accesses a collection of [`Sample`] values from the [`DataReader`] and removes them from the [`DataReader`].
 This operation has the same behavior as [`DataReader::read_next_instance`] except that the samples are 'taken' from the [`DataReader`] such
 that they are no longer accessible via subsequent 'read' or 'take' operations.
		"""
		...

	def get_key_value(self, _key_holder: Any, _handle: InstanceHandle) -> None :
		r"""
 This operation can be used to retrieve the instance key that corresponds to an `handle`.
 The operation will only fill the fields that form the key inside the `key_holder` instance.
 This operation may return [`DdsError::BadParameter`](crate::infrastructure::error::DdsError)
 if the [`InstanceHandle`] `handle` does not correspond to an existing data object known to the [`DataReader`].
		"""
		...

	def lookup_instance(self, _instance: Any) -> InstanceHandle | None  :
		r"""
 This operation takes as a parameter an instance and returns an [`InstanceHandle`] handle
 that can be used in subsequent operations that accept an instance handle as an argument.
 The instance parameter is only used for the purpose of examining the fields that define the
 key. This operation does not register the instance in question. If the instance has not
 been previously registered, or if for any other reason the Service is unable to provide
 an instance handle, the operation will succeed and return [`None`].
		"""
		...

	def get_liveliness_changed_status(self) -> LivelinessChangedStatus :
		r"""
 This operation allows access to the [`LivelinessChangedStatus`].
		"""
		...

	def get_requested_deadline_missed_status(self) -> RequestedDeadlineMissedStatus :
		r"""
 This operation allows access to the [`RequestedDeadlineMissedStatus`].
		"""
		...

	def get_requested_incompatible_qos_status(self) -> RequestedIncompatibleQosStatus :
		r"""
 This operation allows access to the [`RequestedIncompatibleQosStatus`].
		"""
		...

	def get_sample_lost_status(self) -> SampleLostStatus :
		r"""
 This operation allows access to the [`SampleLostStatus`].
		"""
		...

	def get_sample_rejected_status(self) -> SampleRejectedStatus :
		r"""
 This operation allows access to the [`SampleRejectedStatus`].
		"""
		...

	def get_subscription_matched_status(self) -> SubscriptionMatchedStatus :
		r"""
 This operation allows access to the [`SubscriptionMatchedStatus`].
		"""
		...

	def get_topicdescription(self) -> TopicDescription :
		r"""
 This operation returns the [`Topic`] associated with the [`DataReader`]. This is the same [`Topic`]
 that was used to create the [`DataReader`].
		"""
		...

	def get_subscriber(self) -> Subscriber :
		r"""
 This operation returns the [`Subscriber`] to which the [`DataReader`] belongs.
		"""
		...

	def wait_for_historical_data(self, max_wait: Duration) -> None :
		r"""
 This operation blocks the calling thread until either all *historical* data is received, or else the
 duration specified by the `max_wait` parameter elapses, whichever happens first.
 A return value of [`Ok`] indicates that all the *historical* data was received;
 a return value of [`DdsError`](crate::infrastructure::error::DdsError) indicates that `max_wait`
 elapsed before all the data was received.
 This operation is intended only for [`DataReader`] entities that have a non-VOLATILE
 [`DurabilityQosPolicy`](crate::infrastructure::qos_policy::DurabilityQosPolicy).
 As soon as an application enables a non-VOLATILE [`DataReader`] it will start receiving both
 *historical* data, i.e., the data that was written prior to the time the [`DataReader`] joined the
 domain, as well as any new data written by the [`DataWriter`](crate::publication::data_writer::DataWriter) entities.
 There are situations where the application logic may require the application to wait until all *historical*
 data is received.
		"""
		...

	def get_matched_publication_data(self, publication_handle: InstanceHandle) -> PublicationBuiltinTopicData :
		r"""
 This operation retrieves information on a publication that is currently *associated* with the [`DataReader`];
 that is, a publication with a matching [`Topic`] and compatible qos that the application  has not indicated should be ignored by means of the
 [`DomainParticipant::ignore_publication`](crate::domain::domain_participant::DomainParticipant) operation.
 The `publication_handle` must correspond to a publication currently associated with the [`DataReader`] otherwise the operation
 will fail and return [`DdsError::BadParameter`](crate::infrastructure::error::DdsError).
 The operation [`DataReader::get_matched_publications`] can be used to find the publications that are
 currently matched with the [`DataReader`].
		"""
		...

	def get_matched_publications(self) -> list[InstanceHandle] :
		r"""
 This operation retrieves the list of publications currently *associated* with the [`DataReader`]; that is, publications that have a
 matching [`Topic`] and compatible qos that the application has not indicated should be ignored by means of the
 [`DomainParticipant::ignore_publication`](crate::domain::domain_participant::DomainParticipant) operation.
 The handles returned are the ones that are used by the DDS implementation to locally identify
 the corresponding matched [`DataWriter`](crate::publication::data_writer::DataWriter) entities. These handles match the ones that appear in the
 [`SampleInfo::instance_handle`](crate::subscription::sample_info::SampleInfo) when reading the *DCPSPublications* builtin topic.
		"""
		...

	def set_qos(self, qos: DataReaderQos | None ) -> None :
		r"""
 This operation is used to set the QoS policies of the Entity and replacing the values of any policies previously set.
 Certain policies are *immutable;* they can only be set at Entity creation time, or before the entity is made enabled.
 If [`Self::set_qos()`] is invoked after the Entity is enabled and it attempts to change the value of an *immutable* policy, the operation will
 fail and returns [`DdsError::ImmutablePolicy`](crate::infrastructure::error::DdsError).
 Certain values of QoS policies can be incompatible with the settings of the other policies. This operation will also fail if it specifies
 a set of values that once combined with the existing values would result in an inconsistent set of policies. In this case,
 the return value is [`DdsError::InconsistentPolicy`](crate::infrastructure::error::DdsError).
 The existing set of policies are only changed if the [`Self::set_qos()`] operation succeeds. This is indicated by the [`Ok`] return value. In all
 other cases, none of the policies is modified.
 The parameter `qos` can be set to [`QosKind::Default`] to indicate that the QoS of the Entity should be changed to match the current default QoS set in the Entity's factory.
 The operation [`Self::set_qos()`] cannot modify the immutable QoS so a successful return of the operation indicates that the mutable QoS for the Entity has been
 modified to match the current default for the Entity's factory.
		"""
		...

	def get_qos(self) -> DataReaderQos :
		r"""
 This operation allows access to the existing set of [`DataReaderQos`] policies.
		"""
		...

	def set_listener(self, a_listener: Any | None  = None, mask: list[StatusKind] = []) -> None :
		r"""
 This operation installs a Listener on the Entity. The listener will only be invoked on the changes of communication status
 indicated by the specified mask. It is permitted to use [`None`] as the value of the listener. The [`None`] listener behaves
 as a Listener whose operations perform no action.
 Only one listener can be attached to each Entity. If a listener was already set, the operation [`Self::set_listener()`] will replace it with the
 new one. Consequently if the value [`None`] is passed for the listener parameter to the [`Self::set_listener()`] operation, any existing listener
 will be removed.
		"""
		...

	def get_statuscondition(self) -> StatusCondition :
		r"""
 This operation allows access to the [`StatusCondition`] associated with the Entity. The returned
 condition can then be added to a [`WaitSet`](crate::infrastructure::wait_set::WaitSet) so that the application can wait for specific status changes
 that affect the Entity.
		"""
		...

	def get_status_changes(self) -> list[StatusKind] :
		r"""
 This operation retrieves the list of communication statuses in the Entity that are 'triggered.' That is, the list of statuses whose
 value has changed since the last time the application read the status.
 When the entity is first created or if the entity is not enabled, all communication statuses are in the *untriggered* state so the
 list returned by the [`Self::get_status_changes`] operation will be empty.
 The list of statuses returned by the [`Self::get_status_changes`] operation refers to the status that are triggered on the Entity itself
 and does not include statuses that apply to contained entities.
		"""
		...

	def enable(self) -> None :
		r"""
 This operation enables the Entity. Entity objects can be created either enabled or disabled. This is controlled by the value of
 the [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) on the corresponding factory for the Entity.
 The default setting of [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) is such that, by default, it is not necessary to explicitly call enable on newly
 created entities.
 The [`Self::enable()`] operation is idempotent. Calling [`Self::enable()`] on an already enabled Entity returns [`Ok`] and has no effect.
 If an Entity has not yet been enabled, the following kinds of operations may be invoked on it:
 - Operations to set or get an Entity's QoS policies (including default QoS policies) and listener
 - [`Self::get_statuscondition()`]
 - Factory and lookup operations
 - [`Self::get_status_changes()`] and other get status operations (although the status of a disabled entity never changes)
 Other operations may explicitly state that they may be called on disabled entities; those that do not will return the error
 NotEnabled.
 It is legal to delete an Entity that has not been enabled by calling the proper operation on its factory.
 Entities created from a factory that is disabled, are created disabled regardless of the setting of the ENTITY_FACTORY Qos
 policy.
 Calling enable on an Entity whose factory is not enabled will fail and return PRECONDITION_NOT_MET.
 If the `autoenable_created_entities` field of [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) is set to [`true`], the [`Self::enable()`] operation on the factory will
 automatically enable all entities created from the factory.
 The Listeners associated with an entity are not called until the entity is enabled. Conditions associated with an entity that is not
 enabled are *inactive,* that is, the operation [`StatusCondition::get_trigger_value()`] will always return `false`.
		"""
		...

	def get_instance_handle(self) -> InstanceHandle :
		r"""
 This operation returns the [`InstanceHandle`] that represents the Entity.
		"""
		...


class Sample:
	def get_data(self) -> Any :
		...

	def get_sample_info(self) -> SampleInfo :
		...


class TypeKind: 
	boolean = 0
	char8 = 1
	int8 = 2
	uint8 = 3
	int16 = 4
	uint16 = 5
	int32 = 6
	uint32 = 7
	int64 = 8
	uint64 = 9
	float32 = 10
	float64 = 11

class Topic:
	r"""
 The [`Topic`] represents the fact that both publications and subscriptions are tied to a single data-type. Its attributes
 `type_name` defines a unique resulting type for the publication or the subscription. It has also a `name` that allows it to
 be retrieved locally.
	"""
	def get_inconsistent_topic_status(self) -> InconsistentTopicStatus :
		r"""
 This method allows the application to retrieve the [`InconsistentTopicStatus`] of the [`Topic`].
		"""
		...

	def get_participant(self) -> DomainParticipant :
		r"""
 This operation returns the [`DomainParticipant`] to which the [`Topic`] belongs.
		"""
		...

	def get_type_name(self) -> str :
		r"""
 The name of the type used to create the [`Topic`]
		"""
		...

	def get_name(self) -> str :
		r"""
 The name used to create the [`Topic`]
		"""
		...

	def set_qos(self, qos: TopicQos | None ) -> None :
		r"""
 This operation is used to set the QoS policies of the Entity and replacing the values of any policies previously set.
 Certain policies are *immutable;* they can only be set at Entity creation time, or before the entity is made enabled.
 If [`Self::set_qos()`] is invoked after the Entity is enabled and it attempts to change the value of an *immutable* policy, the operation will
 fail and returns [`DdsError::ImmutablePolicy`](crate::infrastructure::error::DdsError).
 Certain values of QoS policies can be incompatible with the settings of the other policies. This operation will also fail if it specifies
 a set of values that once combined with the existing values would result in an inconsistent set of policies. In this case,
 the return value is [`DdsError::InconsistentPolicy`](crate::infrastructure::error::DdsError).
 The existing set of policies are only changed if the [`Self::set_qos()`] operation succeeds. This is indicated by the [`Ok`] return value. In all
 other cases, none of the policies is modified.
 The parameter `qos` can be set to [`QosKind::Default`] to indicate that the QoS of the Entity should be changed to match the current default QoS set in the Entity's factory.
 The operation [`Self::set_qos()`] cannot modify the immutable QoS so a successful return of the operation indicates that the mutable QoS for the Entity has been
 modified to match the current default for the Entity's factory.
		"""
		...

	def get_qos(self) -> TopicQos :
		r"""
 This operation allows access to the existing set of [`TopicQos`] policies.
		"""
		...

	def set_listener(self, a_listener: Any | None  = None, mask: list[StatusKind] = []) -> None :
		r"""
 This operation installs a Listener on the Entity. The listener will only be invoked on the changes of communication status
 indicated by the specified mask. It is permitted to use [`None`] as the value of the listener. The [`None`] listener behaves
 as a Listener whose operations perform no action.
 Only one listener can be attached to each Entity. If a listener was already set, the operation [`Self::set_listener()`] will replace it with the
 new one. Consequently if the value [`None`] is passed for the listener parameter to the [`Self::set_listener()`] operation, any existing listener
 will be removed.
		"""
		...

	def get_statuscondition(self) -> StatusCondition :
		r"""
 This operation allows access to the [`StatusCondition`] associated with the Entity. The returned
 condition can then be added to a [`WaitSet`](crate::infrastructure::wait_set::WaitSet) so that the application can wait for specific status changes
 that affect the Entity.
		"""
		...

	def get_status_changes(self) -> list[StatusKind] :
		r"""
 This operation retrieves the list of communication statuses in the Entity that are 'triggered.' That is, the list of statuses whose
 value has changed since the last time the application read the status.
 When the entity is first created or if the entity is not enabled, all communication statuses are in the *untriggered* state so the
 list returned by the [`Self::get_status_changes`] operation will be empty.
 The list of statuses returned by the [`Self::get_status_changes`] operation refers to the status that are triggered on the Entity itself
 and does not include statuses that apply to contained entities.
		"""
		...

	def enable(self) -> None :
		r"""
 This operation enables the Entity. Entity objects can be created either enabled or disabled. This is controlled by the value of
 the [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) on the corresponding factory for the Entity.
 The default setting of [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) is such that, by default, it is not necessary to explicitly call enable on newly
 created entities.
 The [`Self::enable()`] operation is idempotent. Calling [`Self::enable()`] on an already enabled Entity returns [`Ok`] and has no effect.
 If an Entity has not yet been enabled, the following kinds of operations may be invoked on it:
 - Operations to set or get an Entity's QoS policies (including default QoS policies) and listener
 - [`Self::get_statuscondition()`]
 - Factory and lookup operations
 - [`Self::get_status_changes()`] and other get status operations (although the status of a disabled entity never changes)
 Other operations may explicitly state that they may be called on disabled entities; those that do not will return the error
 NotEnabled.
 It is legal to delete an Entity that has not been enabled by calling the proper operation on its factory.
 Entities created from a factory that is disabled, are created disabled regardless of the setting of the ENTITY_FACTORY Qos
 policy.
 Calling enable on an Entity whose factory is not enabled will fail and return PRECONDITION_NOT_MET.
 If the `autoenable_created_entities` field of [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) is set to [`true`], the [`Self::enable()`] operation on the factory will
 automatically enable all entities created from the factory.
 The Listeners associated with an entity are not called until the entity is enabled. Conditions associated with an entity that is not
 enabled are *inactive,* that is, the operation [`StatusCondition::get_trigger_value()`] will always return `false`.
		"""
		...

	def get_instance_handle(self) -> InstanceHandle :
		r"""
 This operation returns the [`InstanceHandle`] that represents the Entity.
		"""
		...


class TopicDescription:
	pass


class DataWriter:
	r"""
 The [`DataWriter`] allows the application to set the value of the
 data to be published under a given [`Topic`].
	"""
	def register_instance(self, instance: Any) -> InstanceHandle | None  :
		r"""
 This operation informs the Service that the application will be modifying a particular instance.
 It gives an opportunity to the Service to pre-configure itself to improve performance. It takes
 as a parameter an `instance` (to get the key value) and returns an [`InstanceHandle`] that can be
 used in successive [`DataWriter::write`] or [`DataWriter::dispose`] operations.
 This operation should be invoked prior to calling any operation that modifies the instance, such as
 [`DataWriter::write`], [`DataWriter::write_w_timestamp`], [`DataWriter::dispose`] and [`DataWriter::dispose_w_timestamp`].
 The operation may return [`None`] if the Service does not want to allocate any handle for that instance.
 This operation may block and return [`DdsError::Timeout`](crate::infrastructure::error::DdsError) or
 [`DdsError::OutOfResources`](crate::infrastructure::error::DdsError) under the same circumstances
 described for [`DataWriter::write`].
 This operation is idempotent. If it is called for an already registered instance, it just returns the already
 allocated [`InstanceHandle`]. This may be used to lookup and retrieve the handle allocated to a given instance.
 The explicit use of this operation is optional as the application may call directly [`DataWriter::write`]
 and specify no [`InstanceHandle`] to indicate that the *key* should be examined to identify the instance.
		"""
		...

	def register_instance_w_timestamp(self, instance: Any, timestamp: Time) -> InstanceHandle | None  :
		r"""
 This operation performs the same function and return the same values as [`DataWriter::register_instance`] and can be used instead of
 [`DataWriter::register_instance`] in the cases where the application desires to specify the value for the `source_timestamp`.
 The `source_timestamp` potentially affects the relative order in which readers observe events from multiple writers.
 For details see [`DestinationOrderQosPolicy`](crate::infrastructure::qos_policy::DestinationOrderQosPolicy).
		"""
		...

	def unregister_instance(self, instance: Any, handle: InstanceHandle | None  = None) -> None :
		r"""
 This operation reverses the action of [`DataWriter::register_instance`]. It should only be called on an
 instance that is currently registered. This operation should be called just once per instance,
 regardless of how many times [`DataWriter::register_instance`] was called for that instance.
 This operation informs the Service that the [`DataWriter`] is not intending to modify any more of that
 data instance. This operation also indicates that the Service can locally remove all information regarding
 that instance. The application should not attempt to use the handle previously allocated to that instance
 after calling [`DataWriter::unregister_instance`].
 If [`None`] is used as the `handle` argument it indicates that the identity of the instance should
 be automatically deduced from the instance (by means of the key).
 If handle is any value other than [`None`], then it must correspond to the value returned by register_instance when the
 instance (identified by its key) was registered. Otherwise the behavior is as follows:
 - If the handle corresponds to an existing instance but does not correspond to the same instance referred by the 'instance'
 parameter, the operation fails and returns [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
 - If the handle does not correspond to an existing instance the operation fails and returns
 [`DdsError::BadParameter`](crate::infrastructure::error::DdsError).
 If after that, the application wants to modify (write or dispose) the instance, it has to register it again,
 or else pass [`None`] as the `handle` value of those operations.
 This operation does not indicate that the instance is deleted (that is the purpose of dispose). This operation
 just indicates that the [`DataWriter`] no longer has 'anything to say' about the instance.
 [`DataReader`](crate::subscription::data_reader::DataReader) entities that are reading the instance will eventually
 receive a sample with an [`InstanceStateKind::NotAliveNoWriter`](crate::subscription::sample_info::InstanceStateKind)
 if no other [`DataWriter`] entities are writing the instance.
 This operation can affect the ownership of the data instance as described
 in [`OwnershipQosPolicy`](crate::infrastructure::qos_policy::OwnershipQosPolicy).
 If the [`DataWriter`] was the exclusive owner of the instance, then calling [`DataWriter::unregister_instance`]
 will relinquish that ownership.
 This operation may block and return [`DdsError::Timeout`](crate::infrastructure::error::DdsError) under the
 same circumstances described for [`DataWriter::write`].
		"""
		...

	def unregister_instance_w_timestamp(self, instance: Any, handle: InstanceHandle | None , timestamp: Time) -> None :
		r"""
 This operation performs the same function and returns the same values as [`DataWriter::unregister_instance`] and can
 be used instead of [`DataWriter::unregister_instance`] in the cases where the application desires to specify the
 value for the `source_timestamp`.
 The `source_timestamp` potentially affects the relative order in which readers observe events from multiple writers.
 For details see [`DestinationOrderQosPolicy`](crate::infrastructure::qos_policy::DestinationOrderQosPolicy).
		"""
		...

	def get_key_value(self, _key_holder: Any, _handle: InstanceHandle) -> None :
		r"""
 This operation can be used to retrieve the instance key that corresponds to an `handle`. The operation will only fill the
 fields that form the key inside the `key_holder` instance.
 This operation returns [`DdsError::BadParameter`](crate::infrastructure::error::DdsError) if the `handle` does not
 correspond to an existing data object known to the [`DataWriter`].
		"""
		...

	def lookup_instance(self, instance: Any) -> InstanceHandle | None  :
		r"""
 This operation takes as a parameter an instance and returns an [`InstanceHandle`] that can be used in subsequent operations
 that accept an [`InstanceHandle`] as an argument. The `instance` parameter is only used for the purpose of examining the
 fields that define the key.
 This operation does not register the instance in question. If the instance has not been previously registered, or if for any other
 reason the Service is unable to provide an [`InstanceHandle`], the operation will return [`None`].
		"""
		...

	def write(self, data: Any, handle: InstanceHandle | None  = None) -> None :
		r"""
 This operation modifies the value of a data instance. When this operation is used, the Service will automatically supply the
 value of the source timestamp that is made available to [`DataReader`](crate::subscription::data_reader::DataReader)
 objects by means of the [`SampleInfo::source_timestamp`](crate::subscription::sample_info::SampleInfo).
 As a side effect, this operation asserts liveliness on the [`DataWriter`] itself, the [`Publisher`] and the
 [`DomainParticipant`](crate::domain::domain_participant::DomainParticipant).
 If [`None`] is used as the `handle` argument this indicates that the identity of the instance should be automatically deduced
 from the `data` (by means of the key).
 If `handle` is any value other than [`None`], then it must correspond to the value returned by [`DataWriter::register_instance`]
 when the instance (identified by its key) was registered. Otherwise the behavior is as follows:
 - If the `handle` corresponds to an existing instance but does not correspond to the same instance referred by the 'data'
 parameter, the operation fails and returns [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
 - If the `handle` does not correspond to an existing instance the operation fails and returns [`DdsError::BadParameter`](crate::infrastructure::error::DdsError).

 If the [`ReliabilityQosPolicy`](crate::infrastructure::qos_policy::ReliabilityQosPolicyKind) is set to [`ReliabilityQosPolicyKind::Reliable`](crate::infrastructure::qos_policy::ReliabilityQosPolicyKind) this operation
 may block if the modification would cause data to be lost or else cause one of the limits specified in the [`ResourceLimitsQosPolicy`](crate::infrastructure::qos_policy::ResourceLimitsQosPolicy) to be exceeded.
 Under these circumstances, the [`ReliabilityQosPolicy::max_blocking_time`](crate::infrastructure::qos_policy::ReliabilityQosPolicy) configures the maximum time the [`DataWriter::write`] operation may block waiting for space to become
 available. If [`ReliabilityQosPolicy::max_blocking_time`](crate::infrastructure::qos_policy::ReliabilityQosPolicy) elapses before the [`DataWriter`] is able to store the modification without exceeding the limits,
 the write operation will fail and return [`DdsError::Timeout`](crate::infrastructure::error::DdsError).
 Specifically, the [`DataWriter::write`] operation may block in the following situations (note that the list may not be exhaustive),
 even if configured with [`HistoryQosPolicyKind::KeepLast`](crate::infrastructure::qos_policy::HistoryQosPolicyKind):
 - If ([`ResourceLimitsQosPolicy::max_samples`](crate::infrastructure::qos_policy::ResourceLimitsQosPolicy) <
 [`ResourceLimitsQosPolicy::max_instances`](crate::infrastructure::qos_policy::ResourceLimitsQosPolicy) * [`HistoryQosPolicy::depth`](crate::infrastructure::qos_policy::HistoryQosPolicy)), then in the
 situation where the [`ResourceLimitsQosPolicy::max_samples`](crate::infrastructure::qos_policy::ResourceLimitsQosPolicy) resource limit is exhausted
 the Service is allowed to discard samples of some other instance as long as at least one sample remains for such an instance.
 If it is still not possible to make space available to store the modification, the writer is allowed to block.
 - If ([`ResourceLimitsQosPolicy::max_samples`](crate::infrastructure::qos_policy::ResourceLimitsQosPolicy) < [`ResourceLimitsQosPolicy::max_instances`](crate::infrastructure::qos_policy::ResourceLimitsQosPolicy)),
 then the [`DataWriter`] may block regardless of the [`HistoryQosPolicy::depth`](crate::infrastructure::qos_policy::HistoryQosPolicy).

 Instead of blocking, the write operation is allowed to return immediately with the error code [`DdsError::OutOfResources`](crate::infrastructure::error::DdsError)
 provided that the reason for blocking would be that the [`ResourceLimitsQosPolicy`](crate::infrastructure::qos_policy::ResourceLimitsQosPolicy)
 is exceeded and the service determines that even waiting the [`ReliabilityQosPolicy::max_waiting_time`](crate::infrastructure::qos_policy::ReliabilityQosPolicy) has no
 chance of freeing the necessary resources. For example, if the only way to gain the necessary resources would be for the user to unregister an instance.
		"""
		...

	def write_w_timestamp(self, data: Any, handle: InstanceHandle | None , timestamp: Time) -> None :
		r"""
 This operation performs the same function and returns the same values as [`DataWriter::write`] and can
 be used instead of [`DataWriter::write`] in the cases where the application desires to specify the
 value for the `source_timestamp`.
 The `source_timestamp` potentially affects the relative order in which readers observe events from multiple writers.
 For details see [`DestinationOrderQosPolicy`](crate::infrastructure::qos_policy::DestinationOrderQosPolicy).
		"""
		...

	def dispose(self, data: Any, handle: InstanceHandle | None ) -> None :
		r"""
 This operation requests the middleware to delete the data (the actual deletion is postponed until there is no more use for that
 data in the whole system). In general, applications are made aware of the deletion by means of operations on the
 [`DataReader`](crate::subscription::data_reader::DataReader) objects that already knew the instance.
 This operation does not modify the value of the instance. The `handle` parameter is passed just for the purposes of identifying
 the instance.
 When this operation is used, the Service will automatically supply the value of the source timestamp that is made available
 to [`DataReader`](crate::subscription::data_reader::DataReader) objects by means of the
 [`SampleInfo::source_timestamp`](crate::subscription::sample_info::SampleInfo).
 The constraints on the values of the handle parameter and the corresponding error behavior are the same specified for the
 [`DataWriter::unregister_instance`] operation.
 This operation may block and return [`DdsError::Timeout`](crate::infrastructure::error::DdsError) or
 [`DdsError::OutOfResources`](crate::infrastructure::error::DdsError) under the same circumstances described for [`DataWriter::write`].
		"""
		...

	def dispose_w_timestamp(self, data: Any, handle: InstanceHandle | None , timestamp: Time) -> None :
		r"""
 This operation performs the same function and returns the same values as [`DataWriter::dispose`] and can
 be used instead of [`DataWriter::dispose`] in the cases where the application desires to specify the
 value for the `source_timestamp`.
 The `source_timestamp` potentially affects the relative order in which readers observe events from multiple writers.
 For details see [`DestinationOrderQosPolicy`](crate::infrastructure::qos_policy::DestinationOrderQosPolicy).
		"""
		...

	def wait_for_acknowledgments(self, max_wait: Duration) -> None :
		r"""
 This operation blocks the calling thread until either all data written by the [`DataWriter`] is acknowledged by all
 matched [`DataReader`](crate::subscription::data_reader::DataReader) entities that have
 [`ReliabilityQosPolicyKind::Reliable`](crate::infrastructure::qos_policy::ReliabilityQosPolicyKind), or else the duration
 specified by the `max_wait` parameter elapses, whichever happens first. A return value of [`Ok`] indicates that all the samples
 written have been acknowledged by all reliable matched data readers; a return value of [`DdsError::Timeout`](crate::infrastructure::error::DdsError)
 indicates that `max_wait` elapsed before all the data was acknowledged.
 This operation is intended to be used only if the DataWriter has [`ReliabilityQosPolicyKind::Reliable`](crate::infrastructure::qos_policy::ReliabilityQosPolicyKind).
 Otherwise the operation will return immediately with [`Ok`].
		"""
		...

	def get_liveliness_lost_status(self) -> LivelinessLostStatus :
		r"""
 This operation allows access to the [`LivelinessLostStatus`].
		"""
		...

	def get_offered_deadline_missed_status(self) -> OfferedDeadlineMissedStatus :
		r"""
 This operation allows access to the [`OfferedDeadlineMissedStatus`].
		"""
		...

	def get_offered_incompatible_qos_status(self) -> OfferedIncompatibleQosStatus :
		r"""
 This operation allows access to the [`OfferedIncompatibleQosStatus`].
		"""
		...

	def get_publication_matched_status(self) -> PublicationMatchedStatus :
		r"""
 This operation allows access to the [`PublicationMatchedStatus`].
		"""
		...

	def get_topic(self) -> TopicDescription :
		r"""
 This operation returns the [`Topic`] associated with the [`DataWriter`]. This is the same [`Topic`] that was used to create the [`DataWriter`].
		"""
		...

	def get_publisher(self) -> Publisher :
		r"""
 This operation returns the [`Publisher`] to which the [`DataWriter`] object belongs.
		"""
		...

	def assert_liveliness(self) -> None :
		r"""
 This operation manually asserts the liveliness of the [`DataWriter`]. This is used in combination with the
 [`LivelinessQosPolicy`](crate::infrastructure::qos_policy::LivelinessQosPolicy) to indicate to the Service that the entity remains active.
 This operation need only be used if the [`LivelinessQosPolicy`](crate::infrastructure::qos_policy::LivelinessQosPolicy) setting is either
 [`LivelinessQosPolicyKind::ManualByParticipant`](crate::infrastructure::qos_policy::LivelinessQosPolicyKind) or
 [`LivelinessQosPolicyKind::ManualByTopic`](crate::infrastructure::qos_policy::LivelinessQosPolicyKind). Otherwise, it has no effect.
 NOTE: Writing data via the [`DataWriter::write`] operation asserts liveliness on the [`DataWriter`] itself and its
 [`DomainParticipant`](crate::domain::domain_participant::DomainParticipant). Consequently the use of this operation is only needed
 if the application is not writing data regularly.
		"""
		...

	def get_matched_subscription_data(self, subscription_handle: InstanceHandle) -> SubscriptionBuiltinTopicData :
		r"""
 This operation retrieves information on a subscription that is currently *associated* with the [`DataWriter`]; that is, a subscription
 with a matching [`Topic`] and compatible QoS that the application has not indicated should be ignored by means of the
 [`DomainParticipant::ignore_subscription`](crate::domain::domain_participant::DomainParticipant) operation.
 The `subscription_handle` must correspond to a subscription currently associated with the [`DataWriter`], otherwise the operation
 will fail and return [`DdsError::BadParameter`](crate::infrastructure::error::DdsError). The operation [`DataWriter::get_matched_subscriptions`]
 can be used to find the subscriptions that are currently matched with the [`DataWriter`].
		"""
		...

	def get_matched_subscriptions(self) -> list[InstanceHandle] :
		r"""
 This operation retrieves the list of subscriptions currently *associated* with the [`DataWriter`]]; that is, subscriptions that have a
 matching [`Topic`] and compatible QoS that the application has not indicated should be *ignored* by means of the
  [`DomainParticipant::ignore_subscription`](crate::domain::domain_participant::DomainParticipant) operation.
 The handles returned are the ones that are used by the DDS implementation to locally identify the corresponding matched
 [`DataReader`](crate::subscription::data_reader::DataReader) entities. These handles match the ones that appear in the
 [`SampleInfo::instance_handle`](crate::subscription::sample_info::SampleInfo) field when reading the *DCPSSubscriptions* builtin topic.
		"""
		...

	def set_qos(self, qos: DataWriterQos | None ) -> None :
		r"""
 This operation is used to set the QoS policies of the Entity and replacing the values of any policies previously set.
 Certain policies are *immutable;* they can only be set at Entity creation time, or before the entity is made enabled.
 If [`Self::set_qos()`] is invoked after the Entity is enabled and it attempts to change the value of an *immutable* policy, the operation will
 fail and returns [`DdsError::ImmutablePolicy`](crate::infrastructure::error::DdsError).
 Certain values of QoS policies can be incompatible with the settings of the other policies. This operation will also fail if it specifies
 a set of values that once combined with the existing values would result in an inconsistent set of policies. In this case,
 the return value is [`DdsError::InconsistentPolicy`](crate::infrastructure::error::DdsError).
 The existing set of policies are only changed if the [`Self::set_qos()`] operation succeeds. This is indicated by the [`Ok`] return value. In all
 other cases, none of the policies is modified.
 The parameter `qos` can be set to [`QosKind::Default`] to indicate that the QoS of the Entity should be changed to match the current default QoS set in the Entity's factory.
 The operation [`Self::set_qos()`] cannot modify the immutable QoS so a successful return of the operation indicates that the mutable QoS for the Entity has been
 modified to match the current default for the Entity's factory.
		"""
		...

	def get_qos(self) -> DataWriterQos :
		r"""
 This operation allows access to the existing set of [`DataWriterQos`] policies.
		"""
		...

	def set_listener(self, a_listener: Any | None  = None, mask: list[StatusKind] = []) -> None :
		r"""
 This operation installs a Listener on the Entity. The listener will only be invoked on the changes of communication status
 indicated by the specified mask. It is permitted to use [`None`] as the value of the listener. The [`None`] listener behaves
 as a Listener whose operations perform no action.
 Only one listener can be attached to each Entity. If a listener was already set, the operation [`Self::set_listener()`] will replace it with the
 new one. Consequently if the value [`None`] is passed for the listener parameter to the [`Self::set_listener()`] operation, any existing listener
 will be removed.
		"""
		...

	def get_statuscondition(self) -> StatusCondition :
		r"""
 This operation allows access to the [`StatusCondition`] associated with the Entity. The returned
 condition can then be added to a [`WaitSet`](crate::infrastructure::wait_set::WaitSet) so that the application can wait for specific status changes
 that affect the Entity.
		"""
		...

	def get_status_changes(self) -> list[StatusKind] :
		r"""
 This operation retrieves the list of communication statuses in the Entity that are 'triggered.' That is, the list of statuses whose
 value has changed since the last time the application read the status.
 When the entity is first created or if the entity is not enabled, all communication statuses are in the *untriggered* state so the
 list returned by the [`Self::get_status_changes`] operation will be empty.
 The list of statuses returned by the [`Self::get_status_changes`] operation refers to the status that are triggered on the Entity itself
 and does not include statuses that apply to contained entities.
		"""
		...

	def enable(self) -> None :
		r"""
 This operation enables the Entity. Entity objects can be created either enabled or disabled. This is controlled by the value of
 the [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) on the corresponding factory for the Entity.
 The default setting of [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) is such that, by default, it is not necessary to explicitly call enable on newly
 created entities.
 The [`Self::enable()`] operation is idempotent. Calling [`Self::enable()`] on an already enabled Entity returns [`Ok`] and has no effect.
 If an Entity has not yet been enabled, the following kinds of operations may be invoked on it:
 - Operations to set or get an Entity's QoS policies (including default QoS policies) and listener
 - [`Self::get_statuscondition()`]
 - Factory and lookup operations
 - [`Self::get_status_changes()`] and other get status operations (although the status of a disabled entity never changes)
 Other operations may explicitly state that they may be called on disabled entities; those that do not will return the error
 NotEnabled.
 It is legal to delete an Entity that has not been enabled by calling the proper operation on its factory.
 Entities created from a factory that is disabled, are created disabled regardless of the setting of the ENTITY_FACTORY Qos
 policy.
 Calling enable on an Entity whose factory is not enabled will fail and return PRECONDITION_NOT_MET.
 If the `autoenable_created_entities` field of [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) is set to [`true`], the [`Self::enable()`] operation on the factory will
 automatically enable all entities created from the factory.
 The Listeners associated with an entity are not called until the entity is enabled. Conditions associated with an entity that is not
 enabled are *inactive,* that is, the operation [`StatusCondition::get_trigger_value()`] will always return `false`.
		"""
		...

	def get_instance_handle(self) -> InstanceHandle :
		r"""
 This operation returns the [`InstanceHandle`] that represents the Entity.
		"""
		...


class Publisher:
	r"""
 The [`Publisher`] acts on the behalf of one or several [`DataWriter`] objects that belong to it. When it is informed of a change to the
 data associated with one of its [`DataWriter`] objects, it decides when it is appropriate to actually send the data-update message.
 In making this decision, it considers any extra information that goes with the data (timestamp, writer, etc.) as well as the QoS
 of the [`Publisher`] and the [`DataWriter`].
	"""
	def create_datawriter(self, a_topic: TopicDescription, qos: DataWriterQos | None  = None, a_listener: Any | None  = None, mask: list[StatusKind] = []) -> DataWriter :
		r"""
 This operation creates a [`DataWriter`]. The returned [`DataWriter`] will be attached and belongs to the [`Publisher`].
 The [`DataWriter`] returned by this operation has an associated [`Topic`] and a type `Foo`.
 The [`Topic`] passed to this operation must have been created from the same [`DomainParticipant`] that was used to create this
 [`Publisher`]. If the [`Topic`] was created from a different [`DomainParticipant`], the operation will fail and
 return a [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError). In case of failure, the operation
 will return an error and no writer will be created.

 The special value [`QosKind::Default`] can be used to indicate that the [`DataWriter`] should be created with the
 default qos set in the factory. The use of this value is equivalent to the application obtaining the default
 [`DataWriterQos`] by means of the operation [`Publisher::get_default_datawriter_qos`] and using the resulting qos
 to create the [`DataWriter`]. A common application pattern to construct the [`DataWriterQos`] to ensure consistency with the
 associated [`TopicQos`] is to:
 1. Retrieve the QoS policies on the associated [`Topic`] by means of the [`Topic::get_qos`] operation.
 2. Retrieve the default [`DataWriterQos`] qos by means of the [`Publisher::get_default_datawriter_qos`] operation.
 3. Combine those two qos policies using the [`Publisher::copy_from_topic_qos`] and selectively modify policies as desired and
 use the resulting [`DataWriterQos`] to construct the [`DataWriter`].
		"""
		...

	def delete_datawriter(self, a_datawriter: DataWriter) -> None :
		r"""
 This operation deletes a [`DataWriter`] that belongs to the [`Publisher`]. This operation must be called on the
 same [`Publisher`] object used to create the [`DataWriter`]. If [`Publisher::delete_datawriter`] is called on a
 different [`Publisher`], the operation will have no effect and it will return [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
 The deletion of the [`DataWriter`] will automatically unregister all instances. Depending on the settings of the
 [`WriterDataLifecycleQosPolicy`](crate::infrastructure::qos_policy::WriterDataLifecycleQosPolicy), the deletion of the
 [`DataWriter`].
		"""
		...

	def lookup_datawriter(self, topic_name: str) -> DataWriter | None  :
		r"""
 This operation retrieves a previously created [`DataWriter`] belonging to the [`Publisher`] that is attached to a [`Topic`] with a matching
 `topic_name`. If no such [`DataWriter`] exists, the operation will succeed but return [`None`].
 If multiple [`DataWriter`] attached to the [`Publisher`] satisfy this condition, then the operation will return one of them. It is not
 specified which one.
		"""
		...

	def suspend_publications(self) -> None :
		r"""
 This operation indicates to the Service that the application is about to make multiple modifications using [`DataWriter`] objects
 belonging to the [`Publisher`]. It is a hint to the Service so it can optimize its performance by e.g., holding the
 dissemination of the modifications and then batching them. It is not required that the Service use this hint in any way.
 The use of this operation must be matched by a corresponding call to [`Publisher::resume_publications`] indicating that the set of
 modifications has completed. If the [`Publisher`] is deleted before [`Publisher::resume_publications`] is called, any suspended updates yet to
 be published will be discarded.
		"""
		...

	def resume_publications(self) -> None :
		r"""
 This operation indicates to the Service that the application has completed the multiple changes initiated by the previous
 [`Publisher::suspend_publications`] call. This is a hint to the Service that can be used by a Service implementation to
 e.g., batch all the modifications made since the [`Publisher::suspend_publications`].
 The call to [`Publisher::resume_publications`] must match a previous call to [`Publisher::suspend_publications`] otherwise
 the operation will return [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
		"""
		...

	def begin_coherent_changes(self) -> None :
		r"""
 This operation requests that the application will begin a *coherent set* of modifications using [`DataWriter`] objects attached to
 the [`Publisher`]. The *coherent set* will be completed by a matching call to [`Publisher::end_coherent_changes`].
 A *coherent set* is a set of modifications that must be propagated in such a way that they are interpreted at the receivers' side
 as a consistent set of modifications; that is, the receiver will only be able to access the data after all the modifications in the set
 are available at the receiver end. This does not imply that the middleware has to encapsulate all the modifications in a single message;
 it only implies that the receiving applications will behave as if this was the case.
 A connectivity change may occur in the middle of a set of coherent changes; for example, the set of partitions used by the
 [`Publisher`] or one of its subscribers may change, a late-joining [`DataReader`](crate::subscription::data_reader::DataReader)
 may appear on the network, or a communication failure may occur. In the event that such a change prevents an entity from
 receiving the entire set of coherent changes, that entity must behave as if it had received none of the set.
 These calls can be nested. In that case, the coherent set terminates only with the last call to [`Publisher::end_coherent_changes`].
 The support for *coherent changes* enables a publishing application to change the value of several data-instances that could
 belong to the same or different topics and have those changes be seen *atomically* by the readers. This is useful in cases where
 the values are inter-related (for example, if there are two data-instances representing the 'altitude' and 'velocity vector' of the
 same aircraft and both are changed, it may be useful to communicate those values in a way the reader can see both together;
 otherwise, it may e.g., erroneously interpret that the aircraft is on a collision course).
		"""
		...

	def end_coherent_changes(self) -> None :
		r"""
 This operation terminates the *coherent set* initiated by the matching call to [`Publisher::begin_coherent_changes`]. If there is no matching
 call to [`Publisher::begin_coherent_changes`], the operation will return [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
		"""
		...

	def wait_for_acknowledgments(self, max_wait: Duration) -> None :
		r"""
 This operation blocks the calling thread until either all data written by the reliable [`DataWriter`] entities is acknowledged by all
 matched reliable [`DataReader`](crate::subscription::data_reader::DataReader) entities, or else the duration specified by
 the `max_wait` parameter elapses, whichever happens first. A return value of [`Ok`] indicates that all the samples written
 have been acknowledged by all reliable matched data readers; a return value of [`DdsError::Timeout`](crate::infrastructure::error::DdsError)
 indicates that `max_wait` elapsed before all the data was acknowledged.
		"""
		...

	def get_participant(self) -> DomainParticipant :
		r"""
 This operation returns the [`DomainParticipant`] to which the [`Publisher`] belongs.
		"""
		...

	def delete_contained_entities(self) -> None :
		r"""
 This operation deletes all the entities that were created by means of the [`Publisher::create_datawriter`] operations.
 That is, it deletes all contained [`DataWriter`] objects.
 The operation will return [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError) if the any of the
 contained entities is in a state where it cannot be deleted.
 Once this operation returns successfully, the application may delete the [`Publisher`] knowing that it has no
 contained [`DataWriter`] objects
		"""
		...

	def set_default_datawriter_qos(self, qos: DataWriterQos | None ) -> None :
		r"""
 This operation sets the default value of the [`DataWriterQos`] which will be used for newly created [`DataWriter`] entities in
 the case where the qos policies are defaulted in the [`Publisher::create_datawriter`] operation.
 This operation will check that the resulting policies are self consistent; if they are not, the operation will have no effect and
 return [`DdsError::InconsistentPolicy`](crate::infrastructure::error::DdsError).
 The special value [`QosKind::Default`] may be passed to this operation to indicate that the default qos should be
 reset back to the initial values the factory would use, that is the default value of [`DataWriterQos`].
		"""
		...

	def get_default_datawriter_qos(self) -> DataWriterQos :
		r"""
 This operation retrieves the default factory value of the [`DataWriterQos`], that is, the qos policies which will be used for newly created
 [`DataWriter`] entities in the case where the qos policies are defaulted in the [`Publisher::create_datawriter`] operation.
 The values retrieved by this operation will match the set of values specified on the last successful call to
 [`Publisher::set_default_datawriter_qos`], or else, if the call was never made, the default values of [`DataWriterQos`].
		"""
		...

	def set_qos(self, qos: PublisherQos | None ) -> None :
		r"""
 This operation is used to set the QoS policies of the Entity and replacing the values of any policies previously set.
 Certain policies are *immutable;* they can only be set at Entity creation time, or before the entity is made enabled.
 If [`Self::set_qos()`] is invoked after the Entity is enabled and it attempts to change the value of an *immutable* policy, the operation will
 fail and returns [`DdsError::ImmutablePolicy`](crate::infrastructure::error::DdsError).
 Certain values of QoS policies can be incompatible with the settings of the other policies. This operation will also fail if it specifies
 a set of values that once combined with the existing values would result in an inconsistent set of policies. In this case,
 the return value is [`DdsError::InconsistentPolicy`](crate::infrastructure::error::DdsError).
 The existing set of policies are only changed if the [`Self::set_qos()`] operation succeeds. This is indicated by the [`Ok`] return value. In all
 other cases, none of the policies is modified.
 The parameter `qos` can be set to [`QosKind::Default`] to indicate that the QoS of the Entity should be changed to match the current default QoS set in the Entity's factory.
 The operation [`Self::set_qos()`] cannot modify the immutable QoS so a successful return of the operation indicates that the mutable QoS for the Entity has been
 modified to match the current default for the Entity's factory.
		"""
		...

	def get_qos(self) -> PublisherQos :
		r"""
 This operation allows access to the existing set of [`PublisherQos`] policies.
		"""
		...

	def set_listener(self, a_listener: Any | None  = None, mask: list[StatusKind] = []) -> None :
		r"""
 This operation installs a Listener on the Entity. The listener will only be invoked on the changes of communication status
 indicated by the specified mask. It is permitted to use [`None`] as the value of the listener. The [`None`] listener behaves
 as a Listener whose operations perform no action.
 Only one listener can be attached to each Entity. If a listener was already set, the operation [`Self::set_listener()`] will replace it with the
 new one. Consequently if the value [`None`] is passed for the listener parameter to the [`Self::set_listener()`] operation, any existing listener
 will be removed.
		"""
		...

	def get_status_changes(self) -> list[StatusKind] :
		r"""
 This operation retrieves the list of communication statuses in the Entity that are 'triggered.' That is, the list of statuses whose
 value has changed since the last time the application read the status.
 When the entity is first created or if the entity is not enabled, all communication statuses are in the *untriggered* state so the
 list returned by the [`Self::get_status_changes`] operation will be empty.
 The list of statuses returned by the [`Self::get_status_changes`] operation refers to the status that are triggered on the Entity itself
 and does not include statuses that apply to contained entities.
		"""
		...

	def enable(self) -> None :
		r"""
 This operation enables the Entity. Entity objects can be created either enabled or disabled. This is controlled by the value of
 the [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) on the corresponding factory for the Entity.
 The default setting of [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) is such that, by default, it is not necessary to explicitly call enable on newly
 created entities.
 The [`Self::enable()`] operation is idempotent. Calling [`Self::enable()`] on an already enabled Entity returns [`Ok`] and has no effect.
 If an Entity has not yet been enabled, the following kinds of operations may be invoked on it:
 - Operations to set or get an Entity's QoS policies (including default QoS policies) and listener
 - [`Self::get_statuscondition()`]
 - Factory and lookup operations
 - [`Self::get_status_changes()`] and other get status operations (although the status of a disabled entity never changes)
 Other operations may explicitly state that they may be called on disabled entities; those that do not will return the error
 NotEnabled.
 It is legal to delete an Entity that has not been enabled by calling the proper operation on its factory.
 Entities created from a factory that is disabled, are created disabled regardless of the setting of the
 [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy).
 Calling enable on an Entity whose factory is not enabled will fail and return [`DdsError::PreconditionNotMet`](crate::infrastructure::error::DdsError).
 If the `autoenable_created_entities` field of [`EntityFactoryQosPolicy`](crate::infrastructure::qos_policy::EntityFactoryQosPolicy) is set to [`true`], the [`Self::enable()`] operation on the factory will
 automatically enable all entities created from the factory.
 The Listeners associated with an entity are not called until the entity is enabled. Conditions associated with an entity that is not
 enabled are *inactive*, that is, the operation [`StatusCondition::get_trigger_value()`] will always return `false`.
		"""
		...

	def get_instance_handle(self) -> InstanceHandle :
		r"""
 This operation returns the [`InstanceHandle`] that represents the Entity.
		"""
		...

